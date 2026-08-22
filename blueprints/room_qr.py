from io import BytesIO
import qrcode
from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for   

# 2. Import your new database models and services
from api.models.location_model import Room
from api.services.location_service import LocationService

room_qr_bp = Blueprint("room_qr", __name__)
location_service = LocationService()

@room_qr_bp.route("/rooms")
def rooms():
    """
    Display a list of all rooms across all facilities.
    """
    real_rooms = location_service.all_rooms()
    return render_template("room_qr.html", rooms=real_rooms)

@room_qr_bp.route("/rooms/<int:room_id>")
def room_scan(room_id):
    """
    Display the room dashboard for a specific room.
    """
    room = Room.query.get(room_id)
    if room is None:
        return "Room not found", 404

    selected_month = request.args.get("month")

    return render_template(
        "room_scan.html",
        room=room,
        selected_month=selected_month,
        summary={},  # Placeholder until we build room_summary()
        location_label=f"{room.facility.name if room.facility else ''} - {room.name}",
        calendar_view=[],  # Placeholder until we build room_calendar()
    )

@room_qr_bp.route("/rooms/<int:room_id>/qr.png")
def room_qr_code(room_id):
    """
    Generate a QR code for the room that links to its dashboard.
    """
    room = Room.query.get(room_id)
    if room is None:
        return "Room not found", 404

    scan_url = url_for("room_qr.room_scan", room_id=room_id, _external=True)
    image = qrcode.make(scan_url)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png")

@room_qr_bp.route("/rooms/<int:room_id>/check", methods=["POST"])
def submit_room_check(room_id):
    """
    Handle the submission of a room check form.
    """
    room = Room.query.get(room_id)
    if room is None:
        return "Room not found", 404

    note = request.form.get("note", "").strip()
    staff_name = request.form.get("staff_name", "Staff").strip() or "Staff"
    supervisor_email = request.form.get("supervisor_email", "supervisor@example.com")
    
    # Temporarily bypass the email sender and just print to the terminal!
    print(f"📧 [EMAIL SIMULATION] To: {supervisor_email} | Room Check by {staff_name}: {note}")

    flash("Room check was sent to the supervisor.", "success")
    return redirect(url_for("room_qr.room_scan", room_id=room_id))