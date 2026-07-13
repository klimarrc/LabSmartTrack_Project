import os
from io import BytesIO

import qrcode
from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for

import core.messageSender as message_sender

EmailSender = message_sender.EmailSender
ConsoleSender = getattr(message_sender, "ConsoleSender", None)
NotificationSender = getattr(message_sender, "NotificationSender", None)


if ConsoleSender is None:
    class ConsoleSender:
        def send_room_check_report(self, **kwargs):
            print("Room check report:", kwargs)


if NotificationSender is None:
    class NotificationSender:
        def __init__(self, sender):
            self.sender = sender

        def send_room_check_report(self, **kwargs):
            self.sender.send_room_check_report(**kwargs)


room_qr_bp = Blueprint("room_qr", __name__)



ROOMS = {
    "RM-A": {
        "id": "RM-A",
        "name": "Mouse Room A",
        "city": "Winnipeg",
        "facility": "Animal Facility",
        "department": "Comparative Medicine",
        "room_number": "A-120",
        "principal_investigator": "Dr. Chen",
        "strain": "C57BL/6J",
        "weaning_due": 3,
        "breeding": 5,
        "plugs": 2,
        "racks": [
            {"id": "RACK-A1", "name": "Rack A1", "cages": 24, "mice": 72},
            {"id": "RACK-A2", "name": "Rack A2", "cages": 18, "mice": 54},
            {"id": "RACK-A3", "name": "Rack A3", "cages": 6, "mice": 30},
        ],
        "cages": [
            {"id": "CAGE-014", "rack_id": "RACK-A1", "type": "Mating", "status": "Active", "mice": 3},
            {"id": "CAGE-018", "rack_id": "RACK-A2", "type": "Holding", "status": "Active", "mice": 5},
            {"id": "CAGE-021", "rack_id": "RACK-A3", "type": "Weaning", "status": "Active", "mice": 8},
        ],
        "mice": [
            {"id": "M-1001", "sex": "Male", "status": "Breeding"},
            {"id": "M-1002", "sex": "Female", "status": "Pregnant"},
            {"id": "M-1003", "sex": "Female", "status": "With pups"},
        ],
        "breeding_pairs": [
            {"id": "BP-001", "setup": "Trio: 1 male + 2 females", "status": "Active"},
            {"id": "BP-002", "setup": "Pair: 1 male + 1 female", "status": "Active"},
        ],
        "litters": [
            {"id": "L-009", "cage_id": "CAGE-021", "pups": 8, "wean_date": "2026-07-18"},
        ],
    },
    "RM-C": {
        "id": "RM-C",
        "name": "Breeding Room C",
        "city": "Winnipeg",
        "facility": "Breeding Facility",
        "department": "Genetics Core",
        "room_number": "C-210",
        "principal_investigator": "Dr. Santos",
        "strain": "BALB/cJ",
        "weaning_due": 1,
        "breeding": 2,
        "plugs": 1,
        "racks": [
            {"id": "RACK-C1", "name": "Rack C1", "cages": 16, "mice": 38},
            {"id": "RACK-C2", "name": "Rack C2", "cages": 10, "mice": 28},
        ],
        "cages": [
            {"id": "CAGE-033", "rack_id": "RACK-C1", "type": "Mating", "status": "Active", "mice": 2},
            {"id": "CAGE-041", "rack_id": "RACK-C2", "type": "Holding", "status": "Active", "mice": 4},
        ],
        "mice": [
            {"id": "M-2010", "sex": "Male", "status": "Breeding"},
            {"id": "M-2011", "sex": "Female", "status": "Mated"},
        ],
        "breeding_pairs": [
            {"id": "BP-010", "setup": "Pair: 1 male + 1 female", "status": "Active"},
        ],
        "litters": [],
    },
}


def get_room(room_id):
    room = ROOMS.get(room_id)
    if room is None:
        raise ValueError(f"Room with ID '{room_id}' not found.")
    return room


def room_summary(room):
    mouse_count = sum(cage["mice"] for cage in room["cages"])
    return {
        "weaning_due": room["weaning_due"],
        "breeding": room["breeding"],
        "plugs": room["plugs"],
        "racks": len(room["racks"]),
        "cages": len(room["cages"]),
        "mice": mouse_count,
    }


def room_location_label(room):
    return (
        f"{room['city']} / {room['facility']} / {room['department']} / "
        f"{room['name']} / {room['room_number']}"
    )


def notification_service():
    sender_mode = os.getenv("MESSAGE_SENDER_MODE", "console").lower()
    sender = (
        EmailSender(
            smtp_host=os.getenv("SMTP_HOST", "localhost"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            sender_email=os.getenv("SUPERVISOR_EMAIL", "supervisor@example.com"),
        )
        if sender_mode == "email"
        else ConsoleSender()
    )
    return NotificationSender(sender=sender)


@room_qr_bp.route("/rooms")
def rooms():
    return render_template("rooms_qr.html", rooms=ROOMS.values())


@room_qr_bp.route("/rooms/<room_id>")
def room_scan(room_id):
    room = get_room_or_404(room_id)
    if room is None:
        return "Room not found", 404

    return render_template(
        "room_scan.html",
        room=room,
        summary=room_summary(room),
        location_label=room_location_label(room),
    )


@room_qr_bp.route("/rooms/<room_id>/qr.png")
def room_qr_code(room_id):
    room = get_room_or_404(room_id)
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
    room = get_room_or_404(room_id)
    if room is None:
        return "Room not found", 404

    note = request.form.get("note", "").strip()
    staff_name = request.form.get("staff_name", "Staff").strip() or "Staff"
    supervisor_email = os.getenv("SUPERVISOR_EMAIL", "supervisor@example.com")
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
