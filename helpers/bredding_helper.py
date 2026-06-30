import os
from flask import session

# Admin-only cage rates. Keep prices out of user-facing colony pages.
holding = HOLDING_CAGE_PRICE = float(os.getenv("HOLDING_CAGE_PRICE", 1.47))
mating = MATING_CAGE_PRICE = float(os.getenv("MATING_CAGE_PRICE", 2.10))

# Prototype reference data used until the SQLAlchemy models are connected to
# real create/read/update/delete pages.
FACILITIES = [
    {
        "facility_id": "FAC-001",
        "name": "Animal Facility",
        "rooms": [
            {"room_id": "RM-A", "name": "Mouse Room A", "racks": 2, "cages": 38},
            {"room_id": "RM-B", "name": "Mouse Room B", "racks": 1, "cages": 21},
        ],
    },
    {
        "facility_id": "FAC-002",
        "name": "Breeding Facility",
        "rooms": [
            {
                "room_id": "RM-C", 
                "name": "Breeding Room C", 
                "racks": 3, 
                "cages": 44},
        ],
    },
]

# Default breeding pairs, litters, waiting
DEFAULT_BREEDING_PAIRS = [
    {
        "pair_id": "BP-001",
        "facility_id": "FAC-001",
        "facility_name": "Animal Facility",
        "room_id": "RM-A",
        "room_name": "Mouse Room A",
        "principal_investigator": "Dr. Chen",
        "strain": "C57BL/6J",
        "mating_type": "Pair: 1 male + 1 female",
        "sire_id": "M-1001",
        "dam_id": "M-1002",
        "dam2_id": "",
        "cage_id": "CAGE-014",
        "post_litter_male_plan": "Separate male after litter is born",
        "start_date": "2026-05-18",
        "status": "Active",
    },
    {
        "pair_id": "BP-002",
        "facility_id": "FAC-002",
        "facility_name": "Breeding Facility",
        "room_id": "RM-C",
        "room_name": "Breeding Room C",
        "principal_investigator": "Dr. Patel",
        "strain": "BALB/c",
        "mating_type": "Trio: 1 male + 2 females",
        "sire_id": "M-1010",
        "dam_id": "M-1012",
        "dam2_id": "M-1013",
        "cage_id": "CAGE-021",
        "post_litter_male_plan": "Keep male with females after litter is born",
        "start_date": "2026-05-25",
        "status": "Plug check",
    },
]

DEFAULT_LITTERS = [
    {
        "litter_id": "L-001",
        "pair_id": "BP-001",
        "born_date": "2026-06-01",
        "pup_count": 6,
        "wean_due": "2026-06-22",
        "status": "Weaning due later",
    },
    {
        "litter_id": "L-002",
        "pair_id": "BP-002",
        "born_date": "2026-06-08",
        "pup_count": 4,
        "wean_due": "2026-06-29",
        "status": "New litter",
    },
]

DEFAULT_WAITING_FEMALES = [
    {
        "mouse_id": "F-2001",
        "facility_id": "FAC-001",
        "facility_name": "Animal Facility",
        "room_id": "RM-A",
        "room_name": "Mouse Room A",
        "principal_investigator": "Dr. Chen",
        "strain": "C57BL/6J",
        "cage_id": "CAGE-032",
        "age_months": 3,
        "genotype": "+/+",
        "previous_litter_id": "L-009",
        "last_wean_date": "2026-06-12",
        "rest_days": 5,
        "status": "After wean - ready for mating",
    },
    {
        "mouse_id": "F-2002",
        "facility_id": "FAC-001",
        "facility_name": "Animal Facility",
        "room_id": "RM-A",
        "room_name": "Mouse Room A",
        "principal_investigator": "Dr. Chen",
        "strain": "C57BL/6J",
        "cage_id": "CAGE-033",
        "age_months": 4,
        "genotype": "+/-",
        "previous_litter_id": "L-010",
        "last_wean_date": "2026-06-10",
        "rest_days": 7,
        "status": "After wean - ready for mating",
    },
    {
        "mouse_id": "F-2101",
        "facility_id": "FAC-002",
        "facility_name": "Breeding Facility",
        "room_id": "RM-C",
        "room_name": "Breeding Room C",
        "principal_investigator": "Dr. Patel",
        "strain": "BALB/c",
        "cage_id": "CAGE-041",
        "age_months": 3,
        "genotype": "WT",
        "previous_litter_id": "L-011",
        "last_wean_date": "2026-06-14",
        "rest_days": 3,
        "status": "After wean - ready for mating",
    },
]
#  default available males
DEFAULT_AVAILABLE_MALES = [
    {
        "mouse_id": "M-3001",
        "facility_id": "FAC-001",
        "facility_name": "Animal Facility",
        "room_id": "RM-A",
        "room_name": "Mouse Room A",
        "principal_investigator": "Dr. Chen",
        "strain": "C57BL/6J",
        "cage_id": "CAGE-M-032",
        "age_months": 4,
        "genotype": "+/+",
        "status": "Available for mating",
    },
    {
        "mouse_id": "M-3002",
        "facility_id": "FAC-001",
        "facility_name": "Animal Facility",
        "room_id": "RM-A",
        "room_name": "Mouse Room A",
        "principal_investigator": "Dr. Chen",
        "strain": "C57BL/6J",
        "cage_id": "CAGE-M-033",
        "age_months": 5,
        "genotype": "+/-",
        "status": "Available for mating",
    },
    {
        "mouse_id": "M-3101",
        "facility_id": "FAC-002",
        "facility_name": "Breeding Facility",
        "room_id": "RM-C",
        "room_name": "Breeding Room C",
        "principal_investigator": "Dr. Patel",
        "strain": "BALB/c",
        "cage_id": "CAGE-M-041",
        "age_months": 4,
        "genotype": "WT",
        "status": "Available for mating",
    },
]

# Helper functions to retrieve breeding data from session or default values
def all_rooms():
    rooms = []
    for facility in FACILITIES:
        for room in facility["rooms"]:
            rooms.append({
                **room,
                "facility_id": facility["facility_id"],
                "facility_name": facility["name"],
            })
    return rooms

def breeding_pairs_from_session():
    hidden_pair_ids = set(session.get("hidden_breeding_pair_ids", []))
    pairs = []
    for pair in DEFAULT_BREEDING_PAIRS + session.get("breeding_pairs", []):
        pair_record = {**pair}
        pair_record["is_hidden"] = pair_record["pair_id"] in hidden_pair_ids
        pairs.append(pair_record)
    return pairs

def litters_from_session():
    return DEFAULT_LITTERS + session.get("litters", [])

def waiting_females_from_session():
    return DEFAULT_WAITING_FEMALES + session.get("waiting_females", [])

def available_males_from_session():
    return DEFAULT_AVAILABLE_MALES + session.get("available_males", [])

def room_id_for_pair(pair_id):
    pair = next((item for item in breeding_pairs_from_session() if item["pair_id"] == pair_id), None)
    return pair["room_id"] if pair else "all"

def breeding_pair_by_id(pair_id):
    return next((item for item in breeding_pairs_from_session() if item["pair_id"] == pair_id), None)

def females_waiting_for_mating(breeding_pairs):
    active_dam_ids = {
        mouse_id
        for pair in breeding_pairs
        if not pair.get("is_hidden") and pair.get("status", "").lower() != "retired"
        for mouse_id in (pair.get("dam_id"), pair.get("dam2_id"))
        if mouse_id
    }
    return [f for f in waiting_females_from_session() 
            if f["mouse_id"] not in active_dam_ids]

def males_available_for_mating(breeding_pairs):
    active_sire_ids = {
        pair.get("sire_id")
        for pair in breeding_pairs
        if not pair.get("is_hidden") 
        and pair.get("status", "").lower() != "retired"
    }
    hidden_cage_ids = set(session.get("hidden_male_cage_ids", []))
    return [
        m for m in available_males_from_session()
        if m["mouse_id"] not in active_sire_ids 
        and m["cage_id"] not in hidden_cage_ids
    ]

def pi_strain_summary_for_pairs(breeding_pairs):
    grouped = {}
    for pair in breeding_pairs:
        key = (pair["principal_investigator"], 
               pair["strain"], 
               pair["room_name"])
        if key not in grouped:
            grouped[key] = {
                "principal_investigator": pair["principal_investigator"],
                "strain": pair["strain"],
                "room_name": pair["room_name"],
                "mating_count": 0,
                "pair_count": 0,
                "trio_count": 0,
                "cages": set(),
                "mice": set(),
            }
        summary = grouped[key]
        summary["mating_count"] += 1
        if pair.get("mating_type", "").startswith("Trio:"):
            summary["trio_count"] += 1
        else:
            summary["pair_count"] += 1
        if pair.get("cage_id"):
            summary["cages"].add(pair["cage_id"])
        for m_id in (pair.get("sire_id"), pair.get("dam_id"), pair.get("dam2_id")):
            if m_id:
                summary["mice"].add(m_id)
    return [
        {**sum_data, "cage_count": len(sum_data["cages"]), 
         "mouse_count": len(sum_data["mice"]), 
         "cage_ids": ", ".join(sorted(sum_data["cages"]))}
        for sum_data in grouped.values()
    ]

def pi_strain_filter_options(breeding_pairs):
    options = {
        (p["principal_investigator"], p["strain"])
      for p in breeding_pairs}
    return [
        {"value": f"{pi}||{st}", 
         "label": f"{pi} / {st}"} 
        for pi, st in sorted(options)]
