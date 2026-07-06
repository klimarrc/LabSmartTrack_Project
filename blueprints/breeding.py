from io import BytesIO
import qrcode
from flask import Blueprint, redirect, render_template, request, send_file, session, url_for
from blueprints.auth import login_required
import routes

breeding_bp = Blueprint("breeding_views", __name__)


def _all_rooms():
    rooms_fn = getattr(routes, "all_rooms", None)
    if rooms_fn is not None and callable(rooms_fn):
        try:
            return rooms_fn()
        except TypeError:
            pass
    return getattr(routes, "ROOMS", [])

@breeding_bp.route("/breeding")
@login_required
def breeding():
    selected_facility = request.args.get("facility_id", "all")
    selected_room = request.args.get("room_id", "all")
    selected_pi_strain = request.args.get("pi_strain", "all")
    selected_mating_id = request.args.get("mating_id", "").strip()
    show_hidden = request.args.get("show_hidden") == "1"
    
    all_pairs = getattr(routes, "breeding_pairs_from_session", 
                        lambda: session.get("breeding_pairs", []))()
    hidden_count = len([p for p in all_pairs
                         if p.get("is_hidden")])
    breeding_pairs = [p for p in all_pairs 
                      if show_hidden 
                      or not p.get("is_hidden")]
    pi_strain_options = getattr(
        routes,
        "pi_strain_filter_options",
        lambda pairs: sorted(
            {f"{p['principal_investigator']}||{p['strain']}" for p in pairs}
        ),
    )(breeding_pairs)

    if selected_facility != "all":
        breeding_pairs = [
            p for p in breeding_pairs if p["facility_id"] == selected_facility]
    if selected_room != "all":
        breeding_pairs = [
            p for p in breeding_pairs if p["room_id"] == selected_room]
    if selected_pi_strain != "all":
        sel_pi, sel_strain = selected_pi_strain.split("||", 1)
        breeding_pairs = [
                        p for p in breeding_pairs 
                          if p["principal_investigator"] == sel_pi 
                          and p["strain"] == sel_strain]
    if selected_mating_id:
        breeding_pairs = [
            p for p in breeding_pairs 
            if selected_mating_id.lower() in p["pair_id"].lower()]

    waiting_females = getattr(
        routes,
        "females_waiting_for_mating",
        lambda _pairs: [],
    )(all_pairs)
    available_males = getattr(routes, "males_available_for_mating", 
                              lambda _pairs: [])(all_pairs)

    if selected_facility != "all":
        waiting_females = [
            f for f in waiting_females 
            if f["facility_id"] == selected_facility]
        available_males = [
            m for m in available_males 
            if m["facility_id"] == selected_facility]
    if selected_room != "all":
        waiting_females = [
            f for f in waiting_females if f["room_id"] == selected_room]
        available_males = [
            m for m in available_males if m["room_id"] == selected_room]
    if selected_pi_strain != "all":
        sel_pi, sel_strain = selected_pi_strain.split("||", 1)
        waiting_females = [
            f for f in waiting_females 
            if f["principal_investigator"] == sel_pi and f["strain"] == sel_strain]
        available_males = [
            m for m in available_males 
            if m["principal_investigator"] == sel_pi and m["strain"] == sel_strain]

    active_matings = [
        p for p in breeding_pairs 
        if p.get("status", "").lower() != "retired"]
    active_pair_count = len([
        p for p in active_matings
        if p.get("mating_type", "").startswith("Pair:")])
    active_trio_count = len([
        p for p in active_matings 
        if p.get("mating_type", "").startswith("Trio:")])
    visible_pair_ids = {
        p["pair_id"] for p in breeding_pairs}
    litters_from_session = getattr(routes, "litters_from_session", lambda: [])
    litters = [
        l for l in litters_from_session()
        if l["pair_id"] in visible_pair_ids
    ]

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
        pi_strain_summary=getattr(
            routes,
            "pi_strain_summary_for_pairs",
            lambda _pairs: [],
        )(breeding_pairs),
        litter_count=len(litters),
        weaning_due=0, 
        facilities=routes.FACILITIES,
        rooms=_all_rooms(),
        pi_strain_options=pi_strain_options,
        selected_facility=selected_facility, 
        selected_room=selected_room,
        selected_pi_strain=selected_pi_strain, 
        selected_mating_id=selected_mating_id,
        show_hidden=show_hidden,
        hidden_count=hidden_count,
        facility_count=len(routes.FACILITIES)
    )

@breeding_bp.route("/breeding/add-pair", methods=["POST"])
@login_required
def add_breeding_pair():
    room_id = request.form.get("room_id", "")
    room = next((item for item in _all_rooms() if item["room_id"] == room_id), None)
    if not room:
        return redirect(url_for("breeding_views.breeding"))

    new_pair = {
        "pair_id": request.form.get("pair_id", "").strip(),
        "facility_id": room["facility_id"], "facility_name": room["facility_name"],
        "room_id": room["room_id"], "room_name": room["name"],
        "principal_investigator": request.form.get("principal_investigator", "").strip(),
        "strain": request.form.get("strain", "").strip(),
        "mating_type": request.form.get("mating_type", "Pair: 1 male + 1 female"),
        "sire_id": request.form.get("sire_id", "").strip(),
        "sire_source_cage_id": request.form.get("male_source_cage_id", "").strip(),
        "dam_id": request.form.get("dam_id", "").strip(), "dam2_id": request.form.get("dam2_id", "").strip(),
        "cage_id": request.form.get("cage_id", "").strip(),
        "post_litter_male_plan": request.form.get("post_litter_male_plan", "Separate male after litter is born"),
        "start_date": request.form.get("start_date", ""), "status": request.form.get("status", "Active"),
    }
    saved_pairs = session.get("breeding_pairs", [])
    saved_pairs.append(new_pair)
    session["breeding_pairs"] = saved_pairs

    m_source = new_pair["sire_source_cage_id"]
    if m_source:
        hidden_cages = session.get("hidden_male_cage_ids", [])
        if m_source not in hidden_cages:
            hidden_cages.append(m_source)
            session["hidden_male_cage_ids"] = hidden_cages
    return redirect(url_for("breeding_views.breeding", room_id=room_id))

@breeding_bp.route("/breeding/add-litter", methods=["POST"])
@login_required
def add_litter():
    pair_id = request.form.get("pair_id", "").strip()
    new_litter = {
        "litter_id": request.form.get("litter_id", "").strip(), "pair_id": pair_id,
        "born_date": request.form.get("born_date", ""),
        "pup_count": int(request.form.get("pup_count", 0) or 0),
        "wean_due": request.form.get("wean_due", ""), "status": "New litter",
    }
    saved_litters = session.get("litters", [])
    saved_litters.append(new_litter)
    session["litters"] = saved_litters
    return redirect(url_for("breeding_views.breeding", room_id=request.form.get("room_id") or routes.room_id_for_pair(pair_id)))

@breeding_bp.route("/breeding/add-cage-plan", methods=["POST"])
@login_required
def add_cage_plan():
    pair_id = request.form.get("pair_id", "").strip()
    saved_plans = session.get("cage_plans", [])
    saved_plans.append({
        "pair_id": pair_id, "room_id": request.form.get("room_id", ""),
        "plan_type": request.form.get("plan_type", ""), "source_mouse_id": request.form.get("source_mouse_id", ""),
        "new_cage_id": request.form.get("new_cage_id", ""), "female_weaning_cage_id": request.form.get("female_weaning_cage_id", ""),
        "male_weaning_cage_id": request.form.get("male_weaning_cage_id", ""), "move_date": request.form.get("move_date", ""), "status": "Planned",
    })
    session["cage_plans"] = saved_plans
    return redirect(url_for("breeding_views.breeding", room_id=request.form.get("room_id") or routes.room_id_for_pair(pair_id)))

@breeding_bp.route("/breeding/hide-pair", methods=["POST"])
@login_required
def hide_breeding_pair():
    pair_id = request.form.get("pair_id", "").strip()
    room_id = request.form.get("room_id") or routes.room_id_for_pair(pair_id)
    hidden_pair_ids = session.get("hidden_breeding_pair_ids", [])
    if pair_id and pair_id not in hidden_pair_ids:
        hidden_pair_ids.append(pair_id)
        session["hidden_breeding_pair_ids"] = hidden_pair_ids
    return redirect(url_for("breeding_views.breeding", room_id=room_id))

@breeding_bp.route("/breeding/show-pair", methods=["POST"])
@login_required
def show_breeding_pair():
    pair_id = request.form.get("pair_id", "").strip()
    room_id = request.form.get("room_id") or routes.room_id_for_pair(pair_id)
    hidden_pair_ids = [h_id for h_id in session.get("hidden_breeding_pair_ids", []) if h_id != pair_id]
    session["hidden_breeding_pair_ids"] = hidden_pair_ids
    return redirect(url_for("breeding_views.breeding", room_id=room_id, show_hidden=1))

@breeding_bp.route("/breeding/<pair_id>/qr.png")
@login_required
def breeding_pair_qr(pair_id):
    target_url = url_for("breeding_views.breeding_pair_card",
                          pair_id=pair_id, 
                          _external=True)
    image = qrcode.make(target_url)
    image_io = BytesIO()
    image.save(image_io, "PNG")
    image_io.seek(0)
    return send_file(image_io, mimetype="image/png")

@breeding_bp.route("/breeding/<pair_id>/card")
@login_required
def breeding_pair_card(pair_id):
    pair = routes.breeding_pair_by_id(pair_id)
    if not pair:
        return redirect(url_for("breeding_views.breeding"))
    litters_from_session = getattr(routes, "litters_from_session", lambda: [])
    litters = [l for l in litters_from_session() if l["pair_id"] == pair_id]
    return render_template(
        "breeding_card.html", pair=pair, litters=litters,
        qr_url=url_for("breeding_views.breeding_pair_qr", pair_id=pair_id),
        detail_url=url_for("breeding_views.breeding_pair_card", 
                           pair_id=pair_id,
                            _external=True),
    )