"""Login and logout routes."""

from flask import flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user

from api.models.user_model import User
from blueprints.auth import auth_bp
from extensions import limiter


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    """Authenticate an approved, enabled user."""

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    user = User.query.filter_by(email=email).first()

    # Use the same response for unknown accounts and incorrect passwords.
    if user is None or not user.check_password(password):
        flash("Incorrect email or password.", "error")
        return render_template("auth/login.html"), 401

    if user.approval_status == "pending":
        flash("Your account is waiting for administrator approval.", "warning")
        return render_template("auth/login.html"), 403

    if user.approval_status != "approved" or not user.enabled:
        flash("This account cannot access LabSmartTrack.", "error")
        return render_template("auth/login.html"), 403

    session.clear()
    if not login_user(user):
        flash("This account cannot access LabSmartTrack.", "error")
        return render_template("auth/login.html"), 403

    session.permanent = True
    return redirect(url_for("dashboard.dashboard"))


@auth_bp.post("/logout")
def logout():
    """End the authenticated session."""

    logout_user()
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
