"""Login and logout routes."""

from urllib.parse import urlparse

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
)
from sqlalchemy.exc import SQLAlchemyError

from api.models.user_model import User
from blueprints.auth import auth_bp
from database import db
from extensions import limiter


def is_safe_next_url(target):
    """Return whether target is a safe local redirect."""

    if not isinstance(target, str) or not target:
        return False

    parsed_target = urlparse(target)

    return (
        parsed_target.scheme == ""
        and parsed_target.netloc == ""
        and target.startswith("/")
        and not target.startswith("//")
    )


def get_login_error(user, password):
    """Return a login error or None when login is permitted."""

    if user is None or not user.check_password(password):
        return "Incorrect email or password.", "error"

    if user.approval_status == "pending":
        return (
            "Your registration is waiting for administrator approval.",
            "warning",
        )

    if user.approval_status == "rejected":
        return (
            "Your registration was not approved.",
            "error",
        )

    if user.approval_status != "approved":
        return (
            "Your account cannot log in.",
            "error",
        )

    if not user.enabled:
        return "This account is disabled.", "error"

    return None


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("50 per minute", methods=["POST"])
def login():
    """Authenticate an approved and enabled user."""

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        flash(
            "Email and password are required.",
            "error",
        )
        return render_template("auth/login.html"), 400

    try:
        user = User.query.filter_by(email=email).first()
    except SQLAlchemyError:
        db.session.rollback()

        current_app.logger.exception(
            "Database error while processing login"
        )

        flash(
            "Login is temporarily unavailable. Please try again.",
            "error",
        )

        return render_template("auth/login.html"), 500

    error = get_login_error(user, password)

    if error:
        message, category = error
        flash(message, category)

        return render_template("auth/login.html"), 401

    login_user(user)

    next_page = request.args.get("next")

    if is_safe_next_url(next_page):
        return redirect(next_page)

    return redirect(url_for("dashboard.dashboard"))


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """End the authenticated user's session."""

    if current_user.is_authenticated:
        logout_user()

    flash(
        "You have been logged out.",
        "success",
    )

    return redirect(url_for("auth.login"))
