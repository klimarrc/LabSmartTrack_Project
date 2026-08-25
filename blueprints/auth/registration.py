"""Staff registration routes."""

from datetime import date

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from api.models.user_model import User
from api.services.email_service import (
    EmailConfigurationError,
    EmailDeliveryError,
    send_email,
)
from blueprints.auth import auth_bp
from database import db
from extensions import limiter


ALLOWED_REQUESTED_ROLES = {
    "staff",
    "researcher",
    "supervisor",
}


def render_registration(status_code=200):
    """Render registration and preserve submitted values."""

    return (
        render_template(
            "auth/register.html",
            form_data=request.form,
            roles=sorted(ALLOWED_REQUESTED_ROLES),
        ),
        status_code,
    )


def validate_registration(
    email,
    first_name,
    last_name,
    staff_id,
    birth_date_text,
    requested_role,
    password,
    confirmation,
):
    """Return an error message for invalid registration data."""

    required_values = (
        email,
        first_name,
        last_name,
        staff_id,
        birth_date_text,
        requested_role,
        password,
        confirmation,
    )

    if not all(required_values):
        return "Complete all required fields."

    if requested_role not in ALLOWED_REQUESTED_ROLES:
        return "Select a valid requested role."

    if password != confirmation:
        return "Passwords do not match."

    return None


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("50 per minute", methods=["POST"])
def register():
    """Create an account requiring administrator approval."""

    if current_user.is_authenticated:
        return redirect(
            url_for("dashboard.dashboard")
        )

    if request.method == "GET":
        return render_registration()

    email = request.form.get(
        "email",
        "",
    ).strip().lower()

    first_name = request.form.get(
        "first_name",
        "",
    ).strip()

    last_name = request.form.get(
        "last_name",
        "",
    ).strip()

    staff_id = request.form.get(
        "staff_id",
        "",
    ).strip().upper()

    birth_date_text = request.form.get(
        "birth_date",
        "",
    ).strip()

    requested_role = request.form.get(
        "requested_role",
        "",
    ).strip().lower()

    # Do not strip passwords because spaces may be intentional.
    password = request.form.get("password", "")
    confirmation = request.form.get(
        "confirm_password",
        "",
    )

    validation_error = validate_registration(
        email=email,
        first_name=first_name,
        last_name=last_name,
        staff_id=staff_id,
        birth_date_text=birth_date_text,
        requested_role=requested_role,
        password=password,
        confirmation=confirmation,
    )

    if validation_error:
        flash(validation_error, "error")
        return render_registration(400)

    try:
        parsed_birth_date = date.fromisoformat(
            birth_date_text
        )

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

        current_app.logger.info(
            "Registration created: %s",
            user.registration_id,
        )

    except ValueError as error:
        db.session.rollback()

        flash(str(error), "error")
        return render_registration(400)

    except IntegrityError:
        db.session.rollback()

        flash(
            "That email address or staff ID is already registered.",
            "error",
        )

        return render_registration(409)

    except SQLAlchemyError:
        db.session.rollback()

        current_app.logger.exception(
            "Database error during staff registration."
        )

        flash(
            "Registration could not be completed. Please try again.",
            "error",
        )

        return render_registration(500)

    notify_administrator(user)

    return redirect(
        url_for("auth.registration_submitted")
    )


@auth_bp.route(
    "/registration-submitted",
    methods=["GET"],
)
def registration_submitted():
    """Show confirmation after successful registration."""
    account_id = request.args.get("account_id")

    if account_id:
        flash(
            f"Registration submitted. Your registration ID is {account_id}.",
            "success",
        )
    if current_user.is_authenticated:
        return redirect(
            url_for("dashboard.dashboard")
        )

    return render_template(
        "auth/registration_submitted.html"
    )


def notify_administrator(user):
    """Notify the administrator about a pending account."""

    administrator_email = current_app.config.get(
        "ADMIN_EMAIL"
    )

    if not administrator_email:
        current_app.logger.warning(
            "ADMIN_EMAIL is not configured. "
            "Registration notification was not sent."
        )
        return

    base_url = current_app.config.get(
        "APP_BASE_URL",

    )

    review_url = (
        f"{base_url.rstrip('/')}/admin/registrations"
    )
    message = (
        "A new LabSmartTrack registration requires review.\n\n"
        f"Name: {user.full_name}\n"
        f"Email: {user.email}\n"
        f"Staff ID: {user.staff_id}\n"
        f"Requested role: {user.requested_role}\n\n"
        f"Review registration: {review_url}\n"
    )

    try:
        send_email(
            recipient=administrator_email,
            subject="New LabSmartTrack registration",
            text_body=message,
        )

    except (
        EmailConfigurationError,
        EmailDeliveryError,
        ValueError,
    ):
        current_app.logger.exception(
            "Administrator registration email failed."
        )
