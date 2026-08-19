from flask import Blueprint, render_template

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():
    return render_template(
        "dashboard.html",
        room_count=0,
        cage_count=0,
        mouse_count=0,
        weaning_due=0,
        active_matings=0,
        plug_count=0,
    )