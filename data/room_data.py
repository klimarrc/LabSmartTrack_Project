

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
        "room_tasks": [
            {"id": "TASK-001", "title": "Change cages on Rack A1", "due_date": "2026-07-15", "status": "Open"},
            {"id": "TASK-002", "title": "Supervisor review for CAGE-021", "due_date": "2026-07-18", "status": "Open"},
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
        "room_tasks": [
            {"id": "TASK-010", "title": "Check plug records", "due_date": "2026-07-16", "status": "Open"},
            {"id": "TASK-011", "title": "Inventory cage cards", "due_date": "2026-07-22", "status": "Open"},
        ],
    },
}

def get_room_or_404(room_id):
    return ROOMS.get(room_id)