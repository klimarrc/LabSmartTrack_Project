"""
Blueprint for breeding-related views in the Flask application.
This module defines the routes and view functions for managing breeding pairs, 
litters, and related data in the LabSmartTrack application.
"""

from io import BytesIO
import qrcode
from flask import Blueprint, redirect, render_template, request, send_file, session, url_for

# 1. Imports from your services and database models
from api.services.breeding_service import BreedingService
from api.models.mouse_model import Mouse
from api.models.breeding_model import BreedingPair, Litter
from api.models.location_model import Location, Facility, Room, Rack, Cage



# 2. Static reference data (will be replaced by LocationService / MouseService)
from data.breeding import DEMO_WAITING_FEMALES, DEMO_AVAILABLE_MALES, FACILITIES

room_qr_bp = Blueprint("room_qr", __name__)

breeding_bp = Blueprint("breeding_views", __name__)

# 3. Service initialization
breeding_service = BreedingService()


def all_rooms():
    """
    Build a flat list of all rooms across all facilities.
    """
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
        display_pair = pair.to_dict()

        # Map DB fields to the exact keys expected by the UI templates
        display_pair["pair_id"] = pair.breeding_code
        display_pair["is_hidden"] = pair.breeding_code in hidden_pair_ids
        display_pair["room_name"] = display_pair.get("room_name", "Unknown Room")
        display_pair["facility_id"] = display_pair.get("facility_id", "Unknown Facility")

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
    """Retrieve the room ID associated with a given breeding pair."""
    pair = breeding_pair_by_id(pair_id)
    return pair["room_id"] if pair else "all"


def breeding_pair_by_id(pair_id):
    """Find a single breeding pair dictionary by pair_id."""
    return next(
        (pair for pair in breeding_pairs_from_session() if pair["pair_id"] == pair_id),
        None,
    )


def pi_strain_filter_options(pairs):
    """Generate dropdown filter choices for PI and Strain combinations."""
    values = sorted(
        {f"{pair['principal_investigator']}|| {pair['strain']}" for pair in pairs}
    )
    return [
        {"value": value, "label": value.replace("||", " / ")}
        for value in values
    ]


def pi_strain_summary_for_pairs(pairs):
    """
    Build a summary of breeding pairs grouped by (room_name, principal_investigator, strain).
    """
    summary = {}
    for pair in pairs:
        key = (pair.get("room_name"), pair.get("principal_investigator"), pair.get("strain"))
        item = summary.setdefault(
            key,
            {
                "room_name": pair.get("room_name"),
                "principal_investigator": pair.get("principal_investigator"),
                "strain": pair.get("strain"),
                "active_matings": 0,
                "pairs": 0,
                "trios": 0,
                "cages": set(),
                "mice": 0,
            },
        )
        item["active_matings"] += 1
        item["pairs"] += int(pair.get("mating_type", "").startswith("Pair:"))
        item["trios"] += int(pair.get("mating_type", "").startswith("Trio:"))
        if pair.get("cage_id"):
            item["cages"].add(pair["cage_id"])
        item["mice"] += 3 if pair.get("mating_type", "").startswith("Trio:") else 2

    rows = []
    for item in summary.values():
        cages = sorted(item["cages"])
        item["cage_count"] = len(cages)
        item["cage_ids"] = ", ".join(str(c) for c in cages)
        del item["cages"]
        rows.append(item)
    return rows


def filtered_animals(animals, selected_facility, selected_room, selected_pi_strain):
    """Filter animal dictionaries based on facility, room, and PI/strain criteria."""
    filtered = animals
    if selected_facility != "all":
        filtered = [animal for animal in filtered if animal.get("facility_id") == selected_facility]
    if selected_room != "all":
        filtered = [animal for animal in filtered if animal.get("room_id") == selected_room]
    if selected_pi_strain != "all":
        selected_pi, selected_strain = selected_pi_strain.split("||", 1)
        filtered = [
            animal
            for animal in filtered
            if animal.get("principal_investigator") == selected_pi.strip()
            and animal.get("strain") == selected_strain.strip()
        ]
    return filtered