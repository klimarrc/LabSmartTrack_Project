import calendar
import os
from datetime import date, datetime
import core.message_sender as message_sender
from core.message_sender import EmailSender

from data.room_qr_data import ROOMS

def get_room(room_id):
    """
    Fetch a room by its ID from the static ROOMS data.
    Args:
        room_id (str): The ID of the room to fetch.
    Returns:
        dict: The room data if found, else None.
    """
    return ROOMS.get(room_id)


def room_summary(room):
    """
    Generate a summary of the room's status.
    Args:
        room (dict): The room data. 
    Returns:
        dict: A summary containing counts of weaning due, breeding, plugs, racks, cages, and mice.
    """
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
    """
    Generate a human-readable label for the room's location.
    Args:
        room (dict): The room data.
    Returns:
        str: A formatted string representing the room's location.
    """
    return (
        f"{room['city']} / {room['facility']} / {room['department']} / "
        f"{room['name']} / {room['room_number']}"
    )


def room_calendar(room, year=None, month=None):
    """
    Generate a calendar view for the room, highlighting events 
    like weaning and tasks.
    Args:
        room (dict): The room data.
        year (int, optional): The year for the calendar. 
        Defaults to the current year.
        month (int, optional): The month for the calendar.
        Defaults to the current month.
    Returns:
        dict: A dictionary containing the calendar structure and events by day.
    """
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
    """
    Initialize the notification service based on the environment variable.
    Returns:
        Sender: An instance of the configured notification sender.
    """
    sender_mode = os.getenv("MESSAGE_SENDER_MODE", "console").lower()
    console_sender_cls = getattr(message_sender, "ConsoleSender", None)
    if sender_mode != "email" and console_sender_cls is None:
        raise AttributeError("core.message_sender has no 'ConsoleSender' member")

    if sender_mode == "email":
        sender = EmailSender(
            smtp_host=os.getenv("SMTP_HOST", "localhost"),
            smtp_port=int(os.getenv("SMTP_PORT", "25")),
            sender_email=os.getenv("SENDER_EMAIL", "noreply@example.com"),
        )
    else:
        if not callable(console_sender_cls):
            raise TypeError("core.message_sender.ConsoleSender is not callable")
        sender = console_sender_cls()

    return sender
