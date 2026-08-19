from io import BytesIO

import qrcode
from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for


from room_data import ROOMS
from room_service import (
    get_room,
    notification_service,
    room_calendar,
    room_location_label,
    room_summary,
)
from messageSender import ConsoleSender, EmailSender, NotificationSender    


room_qr_bp = Blueprint("room_qr", __name__)


@room_qr_bp.route("/rooms")
def rooms():
    return render_template("room_qr.html", rooms=ROOMS.values())


@room_qr_bp.route("/rooms/<room_id>")
def room_scan(room_id):
    room = get_room(room_id)
    if room is None:
        return "Room not found", 404

    selected_year = request.args.get("year")
    selected_month = request.args.get("month")

    return render_template(
        "room_scan.html",
        room=room,
        summary=room_summary(room),
        location_label=room_location_label(room),
        calendar_view=room_calendar(room, selected_year, selected_month),
    )


@room_qr_bp.route("/rooms/<room_id>/qr.png")
def room_qr_code(room_id):
    room = get_room(room_id)
    if room is None:
        return "Room not found", 404

    scan_url = url_for("room_qr.room_scan", room_id=room_id, _external=True)
    image = qrcode.make(scan_url)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png")


@room_qr_bp.route("/rooms/<room_id>/check", methods=["POST"])
def submit_room_check(room_id):
    room = get_room(room_id)
    if room is None:
        return "Room not found", 404

    note = request.form.get("note", "").strip()
    staff_name = request.form.get("staff_name", "Staff").strip() or "Staff"
    supervisor_email = request.form.get("supervisor_email", "supervisor@example.com")
    summary = room_summary(room)

    notification_service().send_room_check_report(
        room_name=room["name"],
        staff_name=staff_name,
        supervisor_email=supervisor_email,
        weaning_due=summary["weaning_due"],
        breeding=summary["breeding"],
        plugs=summary["plugs"],
        cages=summary["cages"],
        mice=summary["mice"],
        note=note,
    )

    flash("Room check was sent to the supervisor.", "success")
    return redirect(url_for("room_qr.room_scan", room_id=room_id))