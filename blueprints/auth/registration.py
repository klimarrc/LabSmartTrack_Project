"""Staff registration routes."""

import smtplib
from datetime import date

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from blueprints.auth import auth_bp

from api.services.email_service import send_email
from api.models.user_model import User
from database import db
from extensions import limiter


ALLOWED_REQUESTED_ROLES = {"staff", "researcher", "supervisor"}


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per hour")
def register():
    """Create a pending account that requires administrator approval."""

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "GET":
        return render_template("auth/register.html")

    email = request.form.get("email", "").strip().lower()
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    staff_id = request.form.get("staff_id", "").strip()
    birth_date_text = request.form.get("birth_date", "")
    requested_role = request.form.get(
        "requested_role", "staff").strip().lower()
    password = request.form.get("password", "")
    confirmation = request.form.get("confirm_password", "")

    if requested_role not in ALLOWED_REQUESTED_ROLES:
        flash("Invalid requested role.", "error")
        return render_template("auth/register.html", form_data=request.form)

    if password != confirmation:
        flash("Passwords do not match.", "error")
        return render_template("auth/register.html", form_data=request.form)

    try:
        parsed_birth_date = date.fromisoformat(birth_date_text)
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            staff_id=staff_id,
            birth_date=parsed_birth_date,
            requested_role=requested_role,
            role="staff",
            approval_status="pending",
            enabled=True,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        flash(str(error), "error")
        return render_template("auth/register.html", form_data=request.form)
    except IntegrityError:
        db.session.rollback()
        flash("That email or staff ID is already registered.", "error")
        return render_template("auth/register.html", form_data=request.form)
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Staff registration database error.")
        flash("Registration could not be completed. Please try again.", "error")
        return render_template("auth/register.html", form_data=request.form)

    review_url = f"{current_app.config['APP_BASE_URL'].rstrip('/')}/admin/registrations"
    try:
        send_email(
            current_app.config["ADMIN_EMAIL"],
            "New LabSmartTrack registration",

            f"{user.full_name} requested LabSmartTrack access.\n\n"
            f"Staff ID: {user.staff_id}\n"
            f"Requested role: {user.requested_role}\n\n"
            f"Review: {review_url}\n"
        ),

    except (smtplib.SMTPException, OSError, KeyError):
        current_app.logger.exception("Admin registration email failed.")

    flash("Registration submitted. Wait for administrator approval.", "success")
    return redirect(url_for("auth.login"))
