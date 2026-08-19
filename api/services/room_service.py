import calendar
import os
from datetime import date, datetime

from data.room_qr_data import ROOMS

def get_room(room_id):
    return ROOMS.get(room_id)


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


def room_calendar(room, year=None, month=None):
    today = date.today()
    selected_year = int(year or today.year)
    selected_month = int(month or today.month)
    events_by_day = {}

    for litter in room["litters"]:
        event_date = datetime.strptime(litter["wean_date"], "%Y-%m-%d").date()
        if event_date.year == selected_year and event_date.month == selected_month:
            events_by_day.setdefault(event_date.day, []).append(
                {
                    "type": "wean",
                    "label": f"Wean {litter['id']}",
                    "detail": f"{litter['pups']} pups in {litter['cage_id']}",
                }
            )

    for task in room["room_tasks"]:
        task_date = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
        if task_date.year == selected_year and task_date.month == selected_month:
            events_by_day.setdefault(task_date.day, []).append(
                {
                    "type": "task",
                    "label": task["title"],
                    "detail": task["status"],
                }
            )

    weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(selected_year, selected_month)
    return {
        "year": selected_year,
        "month": selected_month,
        "month_name": calendar.month_name[selected_month],
        "weekdays": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        "weeks": weeks,
        "events_by_day": events_by_day,
    }


def notification_service():
    sender_mode = os.getenv("MESSAGE_SENDER_MODE", "console").lower()
    sender = EmailSender() if sender_mode == "email" else ConsoleSender()
    return NotificationSender(sender=sender)
