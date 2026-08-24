"""Password reset request and completion routes."""

import smtplib
import hashlib
import hmac

from flask import current_app, flash, redirect, render_template, request, url_for
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.exc import SQLAlchemyError

#  importing the User model and email service from the api package
from api.models.user_model import User
from api.services.email_service import send_email
from blueprints.auth import auth_bp
from database import db
from extensions import limiter


RESET_SALT = "labsmarttrack-password-reset-v1"


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def _create_token(user):
    password_version = hashlib.sha256(
        user.password_hash.encode("utf-8")
    ).hexdigest()
    return _serializer().dumps(
        {"user_id": user.user_id, "password_version": password_version},
        salt=RESET_SALT,
    )


def _read_token(token):
    return _serializer().loads(token, salt=RESET_SALT, max_age=3600)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("3 per hour")
def forgot_password():
    """Email a time-limited reset link without revealing account existence."""

    if request.method == "GET":
        return render_template("auth/forgot_password.html")

    email = request.form.get("email", "").strip().lower()
    user = User.query.filter_by(email=email).first()

    if user and user.approval_status == "approved" and user.enabled:
        token = _create_token(user)
        reset_url = (
            f"{current_app.config['APP_BASE_URL'].rstrip('/')}"
            f"{url_for('auth.reset_password', token=token)}"
        )
        try:
            send_email(
                user.email,
                "Reset your LabSmartTrack password",
                (
                    f"Hello {user.first_name},\n\n"
                    "Use the link below within one hour to reset your password:\n"
                    f"{reset_url}\n\n"
                    "If you did not request this, ignore this message.\n"
                ),
            )
        except (smtplib.SMTPException, OSError, KeyError):
            current_app.logger.exception("Password reset email failed.")

    flash("If an approved account exists, a reset email has been sent.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
@limiter.limit("5 per hour")
def reset_password(token):
    """Validate a one-hour token and replace the user's password."""

    try:
        data = _read_token(token)
    except SignatureExpired:
        flash("This password-reset link has expired.", "error")
        return redirect(url_for("auth.forgot_password"))
    except BadSignature:
        flash("This password-reset link is invalid.", "error")
        return redirect(url_for("auth.forgot_password"))

    user = db.session.get(User, data.get("user_id"))
    if user is None or not user.enabled or user.approval_status != "approved":
        flash("This password-reset link is invalid.", "error")
        return redirect(url_for("auth.forgot_password"))

    current_password_version = hashlib.sha256(
        user.password_hash.encode("utf-8")
    ).hexdigest()
    if not hmac.compare_digest(
        data.get("password_version", ""), current_password_version
    ):
        flash("This password-reset link has already been used or is invalid.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "GET":
        return render_template("auth/reset_password.html", token=token)

    password = request.form.get("password", "")
    confirmation = request.form.get("confirm_password", "")
    if password != confirmation:
        flash("Passwords do not match.", "error")
        return render_template("auth/reset_password.html", token=token)

    try:
        user.set_password(password)
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        flash(str(error), "error")
        return render_template("auth/reset_password.html", token=token)
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Password reset database error.")
        flash("The password could not be changed. Please try again.", "error")
        return render_template("auth/reset_password.html", token=token)

    flash("Your password was changed. You can now log in.", "success")
    return redirect(url_for("auth.login"))
