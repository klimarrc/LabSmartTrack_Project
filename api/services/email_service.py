"""Secure SMTP email delivery for LabSmartTrack."""

import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr, parseaddr

from flask import current_app


class EmailConfigurationError(RuntimeError):
    """Raised when required SMTP configuration is missing or invalid."""


class EmailDeliveryError(RuntimeError):
    """Raised when the SMTP server cannot deliver an email."""


def _required_config(name):
    """Read a required value from the current Flask configuration."""

    value = current_app.config.get(name)
    if value is None or str(value).strip() == "":
        raise EmailConfigurationError(f"{name} is required for email delivery.")
    return value


def _validate_address(address):
    """Validate a simple mailbox and reject email-header injection."""

    if not isinstance(address, str):
        raise ValueError("Email address must be text.")

    address = address.strip().lower()
    if "\r" in address or "\n" in address:
        raise ValueError("Email address contains invalid characters.")

    display_name, parsed_address = parseaddr(address)
    if display_name or parsed_address != address or address.count("@") != 1:
        raise ValueError("Invalid email address.")

    local_part, domain = address.rsplit("@", 1)
    if not local_part or not domain or "." not in domain:
        raise ValueError("Invalid email address.")

    return address


def _validate_subject(subject):
    """Validate the subject and reject header-injection characters."""

    if not isinstance(subject, str):
        raise ValueError("Email subject must be text.")

    subject = subject.strip()
    if not subject:
        raise ValueError("Email subject is required.")
    if "\r" in subject or "\n" in subject:
        raise ValueError("Email subject contains invalid characters.")
    if len(subject) > 200:
        raise ValueError("Email subject cannot exceed 200 characters.")
    return subject


def _as_bool(value):
    """Convert supported configuration values to a strict boolean."""

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
    raise EmailConfigurationError("Invalid boolean email configuration value.")


def send_email(recipient, subject, text_body, html_body=None):
    """Send an email using the current Flask application's SMTP settings.

    Use SSL for port 465 or STARTTLS for port 587. The two modes cannot be
    enabled together. This function raises a safe custom exception rather than
    returning SMTP credentials or raw server messages to the browser.
    """

    recipient = _validate_address(recipient)
    subject = _validate_subject(subject)

    if not isinstance(text_body, str) or not text_body.strip():
        raise ValueError("Email body is required.")
    if html_body is not None and not isinstance(html_body, str):
        raise ValueError("HTML email body must be text.")

    host = str(_required_config("MAIL_HOST")).strip()
    port = int(_required_config("MAIL_PORT"))
    sender = _validate_address(_required_config("MAIL_FROM"))
    username = current_app.config.get("MAIL_USERNAME")
    password = current_app.config.get("MAIL_PASSWORD")
    sender_name = str(
        current_app.config.get("MAIL_SENDER_NAME", "LabSmartTrack")
    ).strip()
    if not sender_name or "\r" in sender_name or "\n" in sender_name:
        raise EmailConfigurationError("MAIL_SENDER_NAME is invalid.")
    timeout = int(current_app.config.get("MAIL_TIMEOUT", 15))
    use_ssl = _as_bool(current_app.config.get("MAIL_USE_SSL", True))
    use_starttls = _as_bool(current_app.config.get("MAIL_USE_STARTTLS", False))

    if use_ssl and use_starttls:
        raise EmailConfigurationError(
            "MAIL_USE_SSL and MAIL_USE_STARTTLS cannot both be enabled."
        )
    if bool(username) != bool(password):
        raise EmailConfigurationError(
            "MAIL_USERNAME and MAIL_PASSWORD must be configured together."
        )
    if not 1 <= port <= 65535:
        raise EmailConfigurationError("MAIL_PORT is outside the valid range.")
    if not 1 <= timeout <= 120:
        raise EmailConfigurationError("MAIL_TIMEOUT must be from 1 to 120 seconds.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((str(sender_name), sender))
    message["To"] = recipient
    message.set_content(text_body.strip())
    if html_body:
        message.add_alternative(html_body.strip(), subtype="html")

    tls_context = ssl.create_default_context()

    try:
        if use_ssl:
            refused = _send_ssl(
                message, host, port, username, password, timeout, tls_context
            )
        else:
            refused = _send_smtp(
                message,
                host,
                port,
                username,
                password,
                use_starttls,
                timeout,
                tls_context,
            )

        if refused:
            raise EmailDeliveryError("The SMTP server refused the recipient.")
    except (smtplib.SMTPException, OSError, TimeoutError) as error:
        raise EmailDeliveryError("Email delivery failed.") from error


def _send_ssl(message, host, port, username, password, timeout, tls_context):
    """Send through SMTP over SSL, normally on port 465."""

    with smtplib.SMTP_SSL(
        host=host,
        port=port,
        timeout=timeout,
        context=tls_context,
    ) as smtp:
        if username and password:
            smtp.login(username, password)
        return smtp.send_message(message)


def _send_smtp(
    message,
    host,
    port,
    username,
    password,
    use_starttls,
    timeout,
    tls_context,
):
    """Send through SMTP with optional STARTTLS, normally on port 587."""

    with smtplib.SMTP(host=host, port=port, timeout=timeout) as smtp:
        smtp.ehlo()
        if use_starttls:
            smtp.starttls(context=tls_context)
            smtp.ehlo()
        if username and password:
            smtp.login(username, password)
        return smtp.send_message(message)