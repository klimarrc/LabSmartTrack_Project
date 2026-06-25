import os
from io import BytesIO
from functools import wraps

from dotenv import load_dotenv
import qrcode
from flask import Flask, redirect, render_template, request, send_file, session, url_for

from models import db

load_dotenv()  # Load environment variables from .env file
    


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL","sqlite:///lab_smart_track.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


HOLDING_CAGE_PRICE = 1.47
MATING_CAGE_PRICE = 2.10


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
            {"room_id": "RM-C", "name": "Breeding Room C", "racks": 3, "cages": 44},
        ],
    },
]

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


def all_rooms():
    rooms = []
    for facility in FACILITIES:
        for room in facility["rooms"]:
            rooms.append(
                {
                    **room,
                    "facility_id": facility["facility_id"],
                    "facility_name": facility["name"],
                }
            )
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
    pair = next(
        (item for item in breeding_pairs_from_session() if item["pair_id"] == pair_id),
        None,
    )
    return pair["room_id"] if pair else "all"


def breeding_pair_by_id(pair_id):
    return next(
        (item for item in breeding_pairs_from_session() if item["pair_id"] == pair_id),
        None,
    )


def females_waiting_for_mating(breeding_pairs):
    active_dam_ids = {
        mouse_id
        for pair in breeding_pairs
        if not pair.get("is_hidden") and pair.get("status", "").lower() != "retired"
        for mouse_id in (pair.get("dam_id"), pair.get("dam2_id"))
        if mouse_id
    }
    return [
        female
        for female in waiting_females_from_session()
        if female["mouse_id"] not in active_dam_ids
    ]


def males_available_for_mating(breeding_pairs):
    active_sire_ids = {
        pair.get("sire_id")
        for pair in breeding_pairs
        if not pair.get("is_hidden") and pair.get("status", "").lower() != "retired"
    }
    hidden_cage_ids = set(session.get("hidden_male_cage_ids", []))
    return [
        male
        for male in available_males_from_session()
        if male["mouse_id"] not in active_sire_ids
        and male["cage_id"] not in hidden_cage_ids
    ]


def pi_strain_summary_for_pairs(breeding_pairs):
    grouped = {}

    for pair in breeding_pairs:
        key = (pair["principal_investigator"], pair["strain"], pair["room_name"])
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

        for mouse_id in (pair.get("sire_id"), pair.get("dam_id"), pair.get("dam2_id")):
            if mouse_id:
                summary["mice"].add(mouse_id)

    return [
        {
            **summary,
            "cage_count": len(summary["cages"]),
            "mouse_count": len(summary["mice"]),
            "cage_ids": ", ".join(sorted(summary["cages"])),
        }
        for summary in grouped.values()
    ]


def pi_strain_filter_options(breeding_pairs):
    options = {
        (pair["principal_investigator"], pair["strain"])
        for pair in breeding_pairs
    }
    return [
        {
            "value": f"{principal_investigator}||{strain}",
            "label": f"{principal_investigator} / {strain}",
        }
        for principal_investigator, strain in sorted(options)
    ]


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return route_function(*args, **kwargs)

    return wrapper


@app.route("/")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        room_count=0,
        cage_count=0,
        mouse_count=0,
        weaning_due=0,
    )


@app.route("/rooms")
@login_required
def rooms():
    room_count = sum(len(facility["rooms"]) for facility in FACILITIES)
    rack_count = sum(room["racks"] for facility in FACILITIES for room in facility["rooms"])
    cage_count = sum(room["cages"] for facility in FACILITIES for room in facility["rooms"])
    return render_template(
        "rooms.html",
        facilities=FACILITIES,
        facility_count=len(FACILITIES),
        room_count=room_count,
        rack_count=rack_count,
        cage_count=cage_count,
    )


@app.route("/rooms/<int:room_id>/check")
@login_required
def room_check(room_id):
    return render_template("room_check.html", room_id=room_id)


@app.route("/cages")
@login_required
def cages():
    return render_template("cages.html")


@app.route("/cages/<int:cage_id>")
@login_required
def cage_detail(cage_id):
    return render_template("cage_detail.html", cage_id=cage_id)


@app.route("/mice")
@login_required
def mice():
    return render_template("mice.html")


@app.route("/breeding")
@login_required
def breeding():
    selected_facility = request.args.get("facility_id", "all")
    selected_room = request.args.get("room_id", "all")
    selected_pi_strain = request.args.get("pi_strain", "all")
    selected_mating_id = request.args.get("mating_id", "").strip()
    show_hidden = request.args.get("show_hidden") == "1"
    all_breeding_pairs = breeding_pairs_from_session()
    hidden_count = len([pair for pair in all_breeding_pairs if pair.get("is_hidden")])
    breeding_pairs = [
        pair for pair in all_breeding_pairs if show_hidden or not pair.get("is_hidden")
    ]
    pi_strain_options = pi_strain_filter_options(breeding_pairs)

    if selected_facility != "all":
        breeding_pairs = [
            pair for pair in breeding_pairs if pair["facility_id"] == selected_facility
        ]

    if selected_room != "all":
        breeding_pairs = [
            pair for pair in breeding_pairs if pair["room_id"] == selected_room
        ]

    if selected_pi_strain != "all":
        selected_pi, selected_strain = selected_pi_strain.split("||", 1)
        breeding_pairs = [
            pair
            for pair in breeding_pairs
            if pair["principal_investigator"] == selected_pi
            and pair["strain"] == selected_strain
        ]

    if selected_mating_id:
        breeding_pairs = [
            pair
            for pair in breeding_pairs
            if selected_mating_id.lower() in pair["pair_id"].lower()
        ]

    waiting_females = females_waiting_for_mating(all_breeding_pairs)
    available_males = males_available_for_mating(all_breeding_pairs)

    if selected_facility != "all":
        waiting_females = [
            female for female in waiting_females if female["facility_id"] == selected_facility
        ]
        available_males = [
            male for male in available_males if male["facility_id"] == selected_facility
        ]

    if selected_room != "all":
        waiting_females = [
            female for female in waiting_females if female["room_id"] == selected_room
        ]
        available_males = [
            male for male in available_males if male["room_id"] == selected_room
        ]

    if selected_pi_strain != "all":
        selected_pi, selected_strain = selected_pi_strain.split("||", 1)
        waiting_females = [
            female
            for female in waiting_females
            if female["principal_investigator"] == selected_pi
            and female["strain"] == selected_strain
        ]
        available_males = [
            male
            for male in available_males
            if male["principal_investigator"] == selected_pi
            and male["strain"] == selected_strain
        ]

    active_matings = [
        pair for pair in breeding_pairs if pair.get("status", "").lower() != "retired"
    ]
    active_pair_count = len(
        [pair for pair in active_matings if pair.get("mating_type", "").startswith("Pair:")]
    )
    active_trio_count = len(
        [pair for pair in active_matings if pair.get("mating_type", "").startswith("Trio:")]
    )
    holding_cage_count = len(waiting_females) + len(available_males)
    mating_cage_count = len(active_matings)
    visible_pair_ids = {pair["pair_id"] for pair in breeding_pairs}
    litters = [litter for litter in litters_from_session() if litter["pair_id"] in visible_pair_ids]

    return render_template(
        "breeding.html",
        breeding_pairs=breeding_pairs,
        litters=litters,
        active_matings=len(active_matings),
        active_pair_count=active_pair_count,
        active_trio_count=active_trio_count,
        waiting_females=waiting_females,
        waiting_female_count=len(waiting_females),
        available_males=available_males,
        available_male_count=len(available_males),
        holding_cage_price=HOLDING_CAGE_PRICE,
        mating_cage_price=MATING_CAGE_PRICE,
        holding_cage_count=holding_cage_count,
        mating_cage_count=mating_cage_count,
        holding_cage_daily_total=holding_cage_count * HOLDING_CAGE_PRICE,
        mating_cage_daily_total=mating_cage_count * MATING_CAGE_PRICE,
        cage_daily_total=(holding_cage_count * HOLDING_CAGE_PRICE)
        + (mating_cage_count * MATING_CAGE_PRICE),
        pi_strain_summary=pi_strain_summary_for_pairs(breeding_pairs),
        litter_count=len(litters),
        weaning_due=0,
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


@app.route("/breeding/add-pair", methods=["POST"])
@login_required
def add_breeding_pair():
    room_id = request.form.get("room_id", "")
    room = next((item for item in all_rooms() if item["room_id"] == room_id), None)

    if not room:
        return redirect(url_for("breeding"))

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
    }

    saved_pairs = session.get("breeding_pairs", [])
    saved_pairs.append(new_pair)
    session["breeding_pairs"] = saved_pairs

    male_source_cage_id = new_pair["sire_source_cage_id"]
    if male_source_cage_id:
        hidden_male_cage_ids = session.get("hidden_male_cage_ids", [])
        if male_source_cage_id not in hidden_male_cage_ids:
            hidden_male_cage_ids.append(male_source_cage_id)
            session["hidden_male_cage_ids"] = hidden_male_cage_ids

    return redirect(url_for("breeding", room_id=room_id))


@app.route("/breeding/add-litter", methods=["POST"])
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

    saved_litters = session.get("litters", [])
    saved_litters.append(new_litter)
    session["litters"] = saved_litters

    return redirect(url_for("breeding", room_id=request.form.get("room_id") or room_id_for_pair(pair_id)))


@app.route("/breeding/add-cage-plan", methods=["POST"])
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

    return redirect(url_for("breeding", room_id=request.form.get("room_id") or room_id_for_pair(pair_id)))


@app.route("/breeding/hide-pair", methods=["POST"])
@login_required
def hide_breeding_pair():
    pair_id = request.form.get("pair_id", "").strip()
    room_id = request.form.get("room_id") or room_id_for_pair(pair_id)
    hidden_pair_ids = session.get("hidden_breeding_pair_ids", [])

    if pair_id and pair_id not in hidden_pair_ids:
        hidden_pair_ids.append(pair_id)
        session["hidden_breeding_pair_ids"] = hidden_pair_ids

    return redirect(url_for("breeding", room_id=room_id))


@app.route("/breeding/show-pair", methods=["POST"])
@login_required
def show_breeding_pair():
    pair_id = request.form.get("pair_id", "").strip()
    room_id = request.form.get("room_id") or room_id_for_pair(pair_id)
    hidden_pair_ids = [
        hidden_id
        for hidden_id in session.get("hidden_breeding_pair_ids", [])
        if hidden_id != pair_id
    ]
    session["hidden_breeding_pair_ids"] = hidden_pair_ids

    return redirect(url_for("breeding", room_id=room_id, show_hidden=1))


@app.route("/breeding/<pair_id>/qr.png")
@login_required
def breeding_pair_qr(pair_id):
    target_url = url_for("breeding_pair_card", pair_id=pair_id, _external=True)
    image = qrcode.make(target_url)
    image_io = BytesIO()
    image.save(image_io, "PNG")
    image_io.seek(0)
    return send_file(image_io, mimetype="image/png")


@app.route("/breeding/<pair_id>/card")
@login_required
def breeding_pair_card(pair_id):
    pair = breeding_pair_by_id(pair_id)

    if not pair:
        return redirect(url_for("breeding"))

    litters = [
        litter for litter in litters_from_session() if litter["pair_id"] == pair_id
    ]
    return render_template(
        "breeding_card.html",
        pair=pair,
        litters=litters,
        qr_url=url_for("breeding_pair_qr", pair_id=pair_id),
        detail_url=url_for("breeding_pair_card", pair_id=pair_id, _external=True),
    )


@app.route("/reports")
@login_required
def reports():
    return render_template("reports.html")


@app.route("/admin/users")
@login_required
def admin_users():
    return render_template("admin_users.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin_username = os.getenv("ADMIN_USERNAME")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if username == admin_username and password == admin_password:
            session["user"] = {"username": username, "role": "admin"}
            return redirect(url_for("dashboard"))

        error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Initialized LabSmartTrack database.")


if __name__ == "__main__":
    app.run(debug=True)
