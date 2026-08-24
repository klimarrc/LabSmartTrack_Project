"""Administration routes for LabSmartTrack."""

from datetime import datetime, timezone
from functools import wraps

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from api.models.user_model import User
from database import db


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)


def admin_required(view_function):
    """Allow access only to approved administrators."""

    @wraps(view_function)
    @login_required
    def protected_view(*args, **kwargs):
        if (
            current_user.role != "admin"
            or current_user.approval_status != "approved"
            or not current_user.enabled
        ):
            abort(403)

        return view_function(*args, **kwargs)

    return protected_view


@admin_bp.get("/registrations")
@admin_required
def registrations():
    """Display staff registrations waiting for approval."""

    pending_users = (
        User.query
        .filter_by(approval_status="pending")
        .order_by(User.registered_at.asc())
        .all()
    )

    return render_template(
        "admin/registrations.html",
        pending_users=pending_users,
    )


@admin_bp.post("/registrations/<int:user_id>/approve")
@admin_required
def approve_registration(user_id):
    """Approve a pending staff registration."""

    user = db.get_or_404(User, user_id)

    if user.approval_status != "pending":
        flash(
            "This registration has already been reviewed.",
            "warning",
        )
        return redirect(url_for("admin.registrations"))

    # Never allow a registrant to request the admin role.
    allowed_roles = {
        "staff",
        "researcher",
        "supervisor",
    }

    if user.requested_role not in allowed_roles:
        current_app.logger.warning(
            "Invalid requested role for user %s",
            user.user_id,
        )

        flash("The requested role is invalid.", "error")
        return redirect(url_for("admin.registrations"))

    user.approval_status = "approved"
    user.role = user.requested_role
    user.enabled = True
    user.approved_at = datetime.now(timezone.utc)
    user.approved_by_id = current_user.user_id

    try:
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

        current_app.logger.exception(
            "Failed to approve user %s.",
            user.user_id,
        )

        flash(
            "The registration could not be approved.",
            "error",
        )

        return redirect(url_for("admin.registrations"))

    flash(
        f"{user.full_name} was approved and can now log in.",
        "success",
    )

    return redirect(url_for("admin.registrations"))


@admin_bp.post("/registrations/<int:user_id>/reject")
@admin_required
def reject_registration(user_id):
    """Reject a pending staff registration."""

    user = db.get_or_404(User, user_id)

    if user.approval_status != "pending":
        flash(
            "This registration has already been reviewed.",
            "warning",
        )
        return redirect(url_for("admin.registrations"))

    user.approval_status = "rejected"
    user.enabled = False
    user.approved_at = datetime.now(timezone.utc)
    user.approved_by_id = current_user.user_id

    try:
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

        current_app.logger.exception(
            "Failed to reject user %s.",
            user.user_id,
        )

        flash(
            "The registration could not be rejected.",
            "error",
        )

        return redirect(url_for("admin.registrations"))

    flash(
        f"{user.full_name}'s registration was rejected.",
        "success",
    )

    return redirect(url_for("admin.registrations"))