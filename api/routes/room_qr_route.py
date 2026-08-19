# routes.py
import os
from io import BytesIO

import qrcode
from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for

# Import from your separated files
from data import ROOMS, get_room_or_404
from app.services import RoomService, NotificationService

room_qr_bp = Blueprint("room_qr", __name__)

@room_qr_bp.route("/rooms")
def rooms():
    return render_template("rooms_qr.html", rooms=ROOMS.values())


@room_qr_bp.route("/rooms/<room_id>")
def room_scan(room_id):
    room_data = get_room_or_404(room_id)
    if room_data is None:
        return "Room not found", 404

    # Instantiate the service with the room data
    room_service = RoomService(room_data)

    selected_year = request.args.get("year")
    selected_month = request.args.get("month")

    return render_template(
        "room_scan.html",
        room=room_data,
        summary=room_service.get_summary(),
        location_label=room_service.get_location_label(),
        calendar_view=room_service.get_calendar(selected_year, selected_month),
    )


@room_qr_bp.route("/rooms/<room_id>/qr.png")
def room_qr_code(room_id):
    room_data = get_room_or_404(room_id)
    if room_data is None:
        return "Room not found", 404

    scan_url = url_for("room_qr.room_scan", room_id=room_id, _external=True)
    image = qrcode.make(scan_url)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png")


@room_qr_bp.route("/rooms/<room_id>/check", methods=["POST"])
def submit_room_check(room_id):
    room_data = get_room_or_404(room_id)
    if room_data is None:
        return "Room not found", 404

    # Form parsing
    note = request.form.get("note", "").strip()
    staff_name = request.form.get("staff_name", "Staff").strip() or "Staff"

    # Services
    room_service = RoomService(room_data)
    notification_service = NotificationService()

    summary = room_service.get_summary()

    # Send the notification via the service class
    notification_service.send_room_check(
        room_data=room_data,
        summary=summary,
        staff_name=staff_name,
        note=note
    )

    flash("Room check was sent to the supervisor.", "success")
    return redirect(url_for("room_qr.room_scan", room_id=room_id))