
FACILITIES = [
    {
        "facility_id": "FAC-001",
        "name": "Animal Facility",
        "rooms": [
            {"room_id": "RM-A", "name": "Mouse Room A"},
            {"room_id": "RM-C", "name": "Breeding Room C"},
        ],
    }
]

DEMO_BREEDING_PAIRS = [
    {
        "pair_id": "BP-001",
        "facility_id": "FAC-001",
        "facility_name": "Animal Facility",
        "room_id": "RM-A",
        "room_name": "Mouse Room A",
        "principal_investigator": "Dr. Chen",
        "strain": "C57BL/6J",
        "mating_type": "Trio: 1 male + 2 females",
        "sire_id": "M-1001",
        "sire_source_cage_id": "CAGE-010",
        "dam_id": "M-1002",
        "dam2_id": "M-1003",
        "cage_id": "CAGE-014",
        "post_litter_male_plan": "Separate male after litter is born",
        "start_date": "2026-07-01",
        "status": "Active",
        "is_hidden": False,
    },
    {
        "pair_id": "BP-002",
        "facility_id": "FAC-001",
        "facility_name": "Animal Facility",
        "room_id": "RM-C",
        "room_name": "Breeding Room C",
        "principal_investigator": "Dr. Santos",
        "strain": "BALB/cJ",
        "mating_type": "Pair: 1 male + 1 female",
        "sire_id": "M-2010",
        "sire_source_cage_id": "CAGE-030",
        "dam_id": "M-2011",
        "dam2_id": "",
        "cage_id": "CAGE-033",
        "post_litter_male_plan": "Keep male with female after litter is born",
        "start_date": "2026-07-03",
        "status": "Active",
        "is_hidden": False,
    },
]

DEMO_LITTERS = [
    {
        "litter_id": "L-009",
        "pair_id": "BP-001",
        "born_date": "2026-06-27",
        "pup_count": 8,
        "wean_due": "2026-07-18",
        "status": "New litter",
    }
]

DEMO_WAITING_FEMALES = [
    {
        "mouse_id": "M-1104",
        "facility_id": "FAC-001",
        "facility_name": "Animal Facility",
        "room_id": "RM-A",
        "room_name": "Mouse Room A",
        "principal_investigator": "Dr. Chen",
        "strain": "C57BL/6J",
        "genotype": "+/-",
        "age_months": 4,
        "previous_litter_id": "L-006",
        "last_wean_date": "2026-07-01",
        "rest_days": 11,
        "cage_id": "CAGE-018",
        "status": "Available",
    }
]

DEMO_AVAILABLE_MALES = [
    {
        "mouse_id": "M-1201",
        "facility_id": "FAC-001",
        "facility_name": "Animal Facility",
        "room_id": "RM-A",
        "room_name": "Mouse Room A",
        "principal_investigator": "Dr. Chen",
        "strain": "C57BL/6J",
        "genotype": "+/+",
        "age_months": 5,
        "cage_id": "CAGE-022",
        "status": "Available",
    }
]

def get_breeding_pairs_by_room(room_id):
    return [pair for pair in DEMO_BREEDING_PAIRS if pair["room_id"] == room_id]