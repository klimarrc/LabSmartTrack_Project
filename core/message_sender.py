

import os
import smtplib
from email.message import EmailMessage
from typing import Optional, Protocol



class MessageSender(Protocol):
    """Contract for any service that can send a message."""

    def send(self, subject: str, message: str, recipient: str) -> None:
        """Send a message to one recipient."""


class EmailSender:
    """Send LabSmartTrack messages by email."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        sender_email: str,
    ) -> None:
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(smtp_port or os.getenv("SMTP_PORT", "25"))
        self.sender_email = sender_email or os.getenv(
            "SENDER_EMAIL",
            "no-reply@labsmarttrack.local",
        )

    def send(self, subject: str, message: str, recipient: str) -> None:
        """Send an email message to one recipient."""

        email = EmailMessage()
        email["Subject"] = subject
        email["From"] = self.sender_email
        email["To"] = recipient
        email.set_content(message)

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as smtp:
            smtp.send_message(email)

if __name__ == "__main__":
    notifier = EmailSender(
        smtp_host=os.getenv("SMTP_HOST", "localhost"),
        smtp_port=int(os.getenv("SMTP_PORT", "25")),
        sender_email=os.getenv("SENDER_EMAIL", "no-reply@labsmarttrack.local")
    )
    