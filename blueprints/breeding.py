from io import BytesIO
import qrcode
from flask import Blueprint, redirect, render_template, request, send_file, session, url_for

# 1. Import your new service and models!
from api.services.breeding_service import BreedingService
from api.models.mouse_model import Mouse
from api.models.location_model import Cage

# 2. Keep the static data for things we haven't database-ified yet
from data.breeding import DEMO_WAITING_FEMALES, DEMO_AVAILABLE_MALES, FACILITIES

physical_bp = Blueprint("physical_views", __name__)

# 3. Initialize your service!
breeding_service = BreedingService()


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

def breeding_pairs_from_session():
    """Fetch real breeding pairs from the database using the Service."""
    db_pairs = breeding_service.get_breeding_pairs()
    hidden_pair_ids = set(session.get("hidden_breeding_pair_ids", []))
    
    pairs = []
    for pair in db_pairs:
        # Convert the SQLAlchemy model instance to a dictionary for easier manipulation
        display_pair = pair.to_dict()
        
        # Map the DB fields to the exact names your HTML template expects
        display_pair["pair_id"] = pair.breeding_code
        display_pair["is_hidden"] = pair.breeding_code in hidden_pair_ids
        # Provide fallback values so the UI doesn't crash while you transition
        display_pair["room_name"] = display_pair.get
        ("room_name", "Unknown Room")
        display_pair["facility_id"] = display_pair.get
        ("facility_id", "Unknown Facility")
        
        pairs.append(display_pair)
    return pairs


def litters_from_session():
    """Fetch all litters from the database."""
    db_litters = breeding_service.get_litters()
    litters = []
    for litter in db_litters:
        display_litter = litter.to_dict()
        display_litter["pair_id"] = (
            litter.breeding_pair.breeding_code
              if litter.breeding_pair 
              else "Unknown"
        )
        litters.append(display_litter)
    return litters

def room_id_for_pair(pair_id):
    pair = breeding_pair_by_id(pair_id)
    return pair["room_id"] if pair else "all"


def breeding_pair_by_id(pair_id):
    return next((pair for pair in breeding_pairs_from_session()
                 if pair["pair_id"] == pair_id), None)


def pi_strain_filter_options(pairs):
    values = sorted({f"{pair['principal_investigator']}|| {pair['strain']}" 
                     for pair in pairs})
    return [
        {"value": value, "label": value.replace("||", " / ")}
        for value in values
    ]


def pi_strain_summary_for_pairs(pairs):
    """
    Build a summary of breeding pairs grouped by (room_name, 
    principal_investigator, strain)
    Returns a list of dictionaries with the following keys:
        - room_name
        - principal_investigator
        - strain
        - active_matings
        - pairs
        - trios
        - cage_count
        - cage_ids (comma-separated string)
        - mice (total number of mice in the breeding pairs)
        args:
            pairs: list of breeding pair dictionaries
        returns:
            list of summary dictionaries
        example:
            [
                {
                    "room_name": "Room A",
                    "principal_investigator": "Dr. Smith",
                    "strain": "C57BL/6",
                    "active_matings": 5,
                    "pairs": 3,
                    "trios": 2,
                    "cage_count": 4,
                    "cage_ids": "C1, C2, C3, C4",
                    "mice": 12
                },
                
            ]
    """
    # Build a summary of breeding pairs grouped by (room_name, 
    # principal_investigator, strain)
    summary = {}
    for pair in pairs:
        key = (pair["room_name"], pair["principal_investigator"], pair["strain"])
        item = summary.setdefault(
            key,
            {
                "room_name": pair["room_name"],
                "principal_investigator": pair["principal_investigator"],
                "strain": pair["strain"],
                "active_matings": 0,
                "pairs": 0,
                "trios": 0,
                "cages": set(),
                "mice": 0,
            },
        )
        item["active_matings"] += 1
        item["pairs"] += int(pair["mating_type"].startswith("Pair:"))
        item["trios"] += int(pair["mating_type"].startswith("Trio:"))
        item["cages"].add(pair["cage_id"])
        item["mice"] += 3 if pair["mating_type"].startswith("Trio:") else 2

    rows = []
    for item in summary.values():
        cages = sorted(item["cages"])
        item["cage_count"] = len(cages)
        item["cage_ids"] = ", ".join(cages)
        del item["cages"]
        rows.append(item)
    return rows


def filtered_animals(animals, selected_facility, selected_room, selected_pi_strain):
    """
    Filter a list of animals based on selected facility, room, and PI/strain.
    Args:
        animals: list of animal dictionaries
        selected_facility: the facility to filter by
        selected_room: the room to filter by
        selected_pi_strain: the PI/strain to filter by
    Returns:
        list of filtered animal dictionaries
    example:
        filtered_animals(DEMO_WAITING_FEMALES, "Facility A", "Room 1", "Dr. Smith||C57BL/6")

    """
    filtered = animals
    if selected_facility != "all":
        filtered = [animal for animal in filtered if animal["facility_id"] == selected_facility]
    if selected_room != "all":
        filtered = [animal for animal in filtered if animal["room_id"] == selected_room]
    if selected_pi_strain != "all":
        selected_pi, selected_strain = selected_pi_strain.split("||", 1)
        filtered = [
            animal
            for animal in filtered
            if animal["principal_investigator"] == selected_pi and animal["strain"] == selected_strain
        ]
    return filtered