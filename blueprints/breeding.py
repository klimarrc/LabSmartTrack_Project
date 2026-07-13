from io import BytesIO

import qrcode
from flask import Blueprint, redirect, render_template, request, send_file, session, url_for


try:
    from blueprints.auth import login_required
except ImportError:
    def login_required(route_function):
        return route_function


breeding_bp = Blueprint("breeding_views", __name__)


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


def all_rooms():
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
    saved_pairs = session.get("breeding_pairs")
    if saved_pairs is None:
        saved_pairs = DEMO_BREEDING_PAIRS.copy()

    hidden_pair_ids = set(session.get("hidden_breeding_pair_ids", []))
    pairs = []
    for pair in saved_pairs:
        display_pair = pair.copy()
        display_pair["is_hidden"] = display_pair["pair_id"] in hidden_pair_ids
        pairs.append(display_pair)
    return pairs


def litters_from_session():
    return session.get("litters", DEMO_LITTERS.copy())


def room_id_for_pair(pair_id):
    pair = breeding_pair_by_id(pair_id)
    return pair["room_id"] if pair else "all"


def breeding_pair_by_id(pair_id):
    return next((pair for pair in breeding_pairs_from_session() if pair["pair_id"] == pair_id), None)


def pi_strain_filter_options(pairs):
    values = sorted({f"{pair['principal_investigator']}||{pair['strain']}" for pair in pairs})
    return [
        {"value": value, "label": value.replace("||", " / ")}
        for value in values
    ]


def pi_strain_summary_for_pairs(pairs):
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


@breeding_bp.route("/breeding", endpoint="breeding")
@login_required
def breeding():
    selected_facility = request.args.get("facility_id", "all")
    selected_room = request.args.get("room_id", "all")
    selected_pi_strain = request.args.get("pi_strain", "all")
    selected_mating_id = request.args.get("mating_id", "").strip()
    show_hidden = request.args.get("show_hidden") == "1"

    all_pairs = breeding_pairs_from_session()
    hidden_count = len([pair for pair in all_pairs if pair.get("is_hidden")])
    visible_pairs = [pair for pair in all_pairs if show_hidden or not pair.get("is_hidden")]
    pi_strain_options = pi_strain_filter_options(visible_pairs)

    breeding_pairs = visible_pairs
    if selected_facility != "all":
        breeding_pairs = [pair for pair in breeding_pairs if pair["facility_id"] == selected_facility]
    if selected_room != "all":
        breeding_pairs = [pair for pair in breeding_pairs if pair["room_id"] == selected_room]
    if selected_pi_strain != "all":
        selected_pi, selected_strain = selected_pi_strain.split("||", 1)
        breeding_pairs = [
            pair
            for pair in breeding_pairs
            if pair["principal_investigator"] == selected_pi and pair["strain"] == selected_strain
        ]
    if selected_mating_id:
        breeding_pairs = [
            pair for pair in breeding_pairs if selected_mating_id.lower() in pair["pair_id"].lower()
        ]

    active_matings = [pair for pair in breeding_pairs if pair.get("status", "").lower() != "retired"]
    active_pair_count = len([pair for pair in active_matings if pair["mating_type"].startswith("Pair:")])
    active_trio_count = len([pair for pair in active_matings if pair["mating_type"].startswith("Trio:")])
    visible_pair_ids = {pair["pair_id"] for pair in breeding_pairs}
    litters = [litter for litter in litters_from_session() if litter["pair_id"] in visible_pair_ids]
    weaning_due = len([litter for litter in litters if litter.get("wean_due")])

    waiting_females = filtered_animals(
        DEMO_WAITING_FEMALES,
        selected_facility,
        selected_room,
        selected_pi_strain,
    )
    available_males = filtered_animals(
        [
            male
            for male in DEMO_AVAILABLE_MALES
            if male["cage_id"] not in session.get("hidden_male_cage_ids", [])
        ],
        selected_facility,
        selected_room,
        selected_pi_strain,
    )

    return render_template(
        "breeding/breeding.html",
        breeding_pairs=breeding_pairs,
        litters=litters,
        active_matings=len(active_matings),
        active_pair_count=active_pair_count,
        active_trio_count=active_trio_count,
        waiting_females=waiting_females,
        waiting_female_count=len(waiting_females),
        available_males=available_males,
        available_male_count=len(available_males),
        pi_strain_summary=pi_strain_summary_for_pairs(breeding_pairs),
        litter_count=len(litters),
        weaning_due=weaning_due,
        facilities=FACILITIES,
        rooms=all_rooms(),
        pi_strain_options=pi_strain_options,
        selected_facility=selected_facility,
        selected_room=selected_room,
        selected_pi_strain=selected_pi_strain,
        selected_mating_id=selected_mating_id,
        show_hidden=show_hidden,
        hidden_count=hidden_count,
        facility_count=len(FACILITIES),
    )


@breeding_bp.route("/breeding/add-pair", methods=["POST"], endpoint="add_breeding_pair")
@login_required
def add_breeding_pair():
    room_id = request.form.get("room_id", "")
    room = next((item for item in all_rooms() if item["room_id"] == room_id), None)
    if room is None:
        return redirect(url_for("breeding_views.breeding"))

    new_pair = {
        "pair_id": request.form.get("pair_id", "").strip(),
        "facility_id": room["facility_id"],
        "facility_name": room["facility_name"],
        "room_id": room["room_id"],
        "room_name": room["name"],
        "principal_investigator": request.form.get("principal_investigator", "").strip(),
        "strain": request.form.get("strain", "").strip(),
        "mating_type": request.form.get("mating_type", "Pair: 1 male + 1 female"),
        "sire_id": request.form.get("sire_id", "").strip(),
        "sire_source_cage_id": request.form.get("male_source_cage_id", "").strip(),
        "dam_id": request.form.get("dam_id", "").strip(),
        "dam2_id": request.form.get("dam2_id", "").strip(),
        "cage_id": request.form.get("cage_id", "").strip(),
        "post_litter_male_plan": request.form.get(
            "post_litter_male_plan",
            "Separate male after litter is born",
        ),
        "start_date": request.form.get("start_date", ""),
        "status": request.form.get("status", "Active"),
        "is_hidden": False,
    }

    saved_pairs = session.get("breeding_pairs", DEMO_BREEDING_PAIRS.copy())
    saved_pairs.append(new_pair)
    session["breeding_pairs"] = saved_pairs

    male_source_cage_id = new_pair["sire_source_cage_id"]
    if male_source_cage_id:
        hidden_cage_ids = session.get("hidden_male_cage_ids", [])
        if male_source_cage_id not in hidden_cage_ids:
            hidden_cage_ids.append(male_source_cage_id)
            session["hidden_male_cage_ids"] = hidden_cage_ids

    return redirect(url_for("breeding_views.breeding", room_id=room_id))


@breeding_bp.route("/breeding/add-litter", methods=["POST"], endpoint="add_litter")
@login_required
def add_litter():
    pair_id = request.form.get("pair_id", "").strip()
    new_litter = {
        "litter_id": request.form.get("litter_id", "").strip(),
        "pair_id": pair_id,
        "born_date": request.form.get("born_date", ""),
        "pup_count": int(request.form.get("pup_count", 0) or 0),
        "wean_due": request.form.get("wean_due", ""),
        "status": "New litter",
    }
    saved_litters = session.get("litters", DEMO_LITTERS.copy())
    saved_litters.append(new_litter)
    session["litters"] = saved_litters
    return redirect(url_for("breeding_views.breeding", room_id=request.form.get("room_id") or room_id_for_pair(pair_id)))


@breeding_bp.route("/breeding/add-cage-plan", methods=["POST"], endpoint="add_cage_plan")
@login_required
def add_cage_plan():
    pair_id = request.form.get("pair_id", "").strip()
    saved_plans = session.get("cage_plans", [])
    saved_plans.append(
        {
            "pair_id": pair_id,
            "room_id": request.form.get("room_id", ""),
            "plan_type": request.form.get("plan_type", ""),
            "source_mouse_id": request.form.get("source_mouse_id", ""),
            "new_cage_id": request.form.get("new_cage_id", ""),
            "female_weaning_cage_id": request.form.get("female_weaning_cage_id", ""),
            "male_weaning_cage_id": request.form.get("male_weaning_cage_id", ""),
            "move_date": request.form.get("move_date", ""),
            "status": "Planned",
        }
    )
    session["cage_plans"] = saved_plans
    return redirect(url_for("breeding_views.breeding", room_id=request.form.get("room_id") or room_id_for_pair(pair_id)))


@breeding_bp.route("/breeding/hide-pair", methods=["POST"], endpoint="hide_breeding_pair")
@login_required
def hide_breeding_pair():
    pair_id = request.form.get("pair_id", "").strip()
    room_id = request.form.get("room_id") or room_id_for_pair(pair_id)
    hidden_pair_ids = session.get("hidden_breeding_pair_ids", [])
    if pair_id and pair_id not in hidden_pair_ids:
        hidden_pair_ids.append(pair_id)
        session["hidden_breeding_pair_ids"] = hidden_pair_ids
    return redirect(url_for("breeding_views.breeding", room_id=room_id))


@breeding_bp.route("/breeding/show-pair", methods=["POST"], endpoint="show_breeding_pair")
@login_required
def show_breeding_pair():
    pair_id = request.form.get("pair_id", "").strip()
    room_id = request.form.get("room_id") or room_id_for_pair(pair_id)
    session["hidden_breeding_pair_ids"] = [
        hidden_id for hidden_id in session.get("hidden_breeding_pair_ids", []) if hidden_id != pair_id
    ]
    return redirect(url_for("breeding_views.breeding", room_id=room_id, show_hidden=1))


@breeding_bp.route("/breeding/<pair_id>/qr.png", endpoint="breeding_pair_qr")
@login_required
def breeding_pair_qr(pair_id):
    target_url = url_for("breeding_views.breeding_pair_card", pair_id=pair_id, _external=True)
    image = qrcode.make(target_url)
    image_io = BytesIO()
    image.save(image_io, "PNG")
    image_io.seek(0)
    return send_file(image_io, mimetype="image/png")


@breeding_bp.route("/breeding/<pair_id>/card", endpoint="breeding_pair_card")
@login_required
def breeding_pair_card(pair_id):
    pair = breeding_pair_by_id(pair_id)
    if pair is None:
        return redirect(url_for("breeding_views.breeding"))

    litters = [litter for litter in litters_from_session() if litter["pair_id"] == pair_id]
    return render_template(
        "breeding/breeding_card.html",
        pair=pair,
        litters=litters,
        qr_url=url_for("breeding_views.breeding_pair_qr", pair_id=pair_id),
        detail_url=url_for("breeding_views.breeding_pair_card", pair_id=pair_id, _external=True),
    )
