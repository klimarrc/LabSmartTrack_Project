from io import BytesIO
import qrcode
from flask import Blueprint, redirect, render_template, request, send_file, session, url_for

# 1. Import your models so SQLAlchemy knows what tables to create!
from api.services.breeding_service import BreedingService
from api.models.mouse_model import Mouse
from api.models.location_model import Cage
from api.services.location_service import LocationService
from data.breeding import FACILITIES



physical_bp = Blueprint("physical_views", __name__)

# 2. Initialize your service!
location_service = LocationService()
breeding_service = BreedingService()

def all_facilities():
    """
    Build a flat list of all facilities.
    Returns:
        list of facility dictionaries with the following keys:
            - facility_id
            - name
    """
    facilities = []
    for location in FACILITIES:
        facilities.append(
            {
                "facility_id": facility["facility_id"],
                "name": facility["name"],
            }
        )
    return facilities

def all_rooms():
    """
    Build a flat list of all rooms across all facilities.
    Returns:
        list of room dictionaries with the following keys:
            - facility_id
            - facility_name
            - room_id
            - name
    """
    # Build a flat list of all rooms across all facilities
    rooms = []
    for facility in FACILITIES:
        for room in facility["rooms"]:
            rooms.append(
                {
                    "facility_id": facility["facility_id"],
                    "facility_name": facility["name"],
                    "room_id": room["room_id"],
                    "name": room["name"],
                }
            )
    return rooms
