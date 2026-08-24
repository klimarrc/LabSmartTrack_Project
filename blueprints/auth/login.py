"""Login and logout routes."""

import logging

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError

from api.models.user_model import User
from extensions import limiter
from blueprints.auth import auth_bp
from database import db

logger = logging.getLogger(__name__)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def login():
    """Authenticate an approved and enabled user."""

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    try:
        user = User.query.filter_by(email=email).first()
        error = get_login_error(user, password)

        if error:
            message, category = error
            flash(message, category)
            return render_template("auth/login.html")

        login_user(user)
        return redirect(url_for("dashboard.dashboard"))

    except SQLAlchemyError:
        db.session.rollback()

        # Record technical details in the server log,
        # but do not expose them to the browser.
        logger.exception("Database error during login")

        flash(
            "Login is temporarily unavailable. Please try again.",
            "error",
        )

        return render_template("auth/login.html"), 500


def get_login_error(user, password):
    """Return an error message or None when login is permitted."""

    if user is None or not user.check_password(password):
        return "Incorrect email or password.", "error"

    if user.approval_status == "pending":
        return (
            "Your registration is waiting for administrator approval.",
            "warning",
        )

    if user.approval_status == "rejected":
        return "Your registration was not approved.", "error"

    if user.approval_status != "approved":
        return "Your account cannot log in.", "error"

    if not user.enabled:
        return "This account is disabled.", "error"

    return None


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """End the authenticated user's session."""

    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
