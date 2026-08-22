""" Dashboard blueprint for the LabSmartTrack application. """

from flask import Blueprint, render_template

# Import your models so we can query the database
from api.models.location_model import Room, Cage
from api.models.mouse_model import Mouse

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def dashboard():
    """Render the dashboard page with counts of rooms, cages, and mice."""
    # Query the database for the total counts
    total_rooms = Room.query.count()
    total_cages = Cage.query.count()
    total_mice = Mouse.query.count()

    return render_template(
        "dashboard.html",
        room_count=total_rooms,
        cage_count=total_cages,
        mouse_count=total_mice,
        weaning_due=0,  # We can build the logic for this later!
    )