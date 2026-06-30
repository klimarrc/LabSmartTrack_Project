from flask import Blueprint, render_template
from blueprints.auth import login_required
from routes import FACILITIES, HOLDING_CAGE_PRICE, MATING_CAGE_PRICE

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html",
                            room_count=0, 
                            cage_count=0, 
                            mouse_count=0, 
                            weaning_due=0)

@main_bp.route("/rooms")
@login_required
def rooms():
    room_count = sum(len(f["rooms"]) for f in FACILITIES)
    rack_count = sum(r["racks"] for f in FACILITIES for r in f["rooms"])
    cage_count = sum(r["cages"] for f in FACILITIES for r in f["rooms"])
    return render_template("rooms.html", facilities=FACILITIES, 
                                        facility_count=len(FACILITIES),
                                        room_count=room_count, 
                                        rack_count=rack_count, 
                                        cage_count=cage_count)

@main_bp.route("/rooms/<int:room_id>/check")
@login_required
def room_check(room_id):
    return render_template("room_check.html", room_id=room_id)

@main_bp.route("/cages")
@login_required
def cages():
    return render_template("cages.html")

@main_bp.route("/cages/<int:cage_id>")
@login_required
def cage_detail(cage_id):
    return render_template("cage_detail.html", cage_id=cage_id)

@main_bp.route("/mice")
@login_required
def mice():
    return render_template("mice.html")

@main_bp.route("/reports")
@login_required
def reports():
    return render_template("reports.html")

@main_bp.route("/admin/users")
@login_required
def admin_users():
    return render_template("admin_users.html", 
                           holding_cage_price=HOLDING_CAGE_PRICE, 
                           mating_cage_price=MATING_CAGE_PRICE)