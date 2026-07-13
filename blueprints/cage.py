from io import BytesIO

import qrcode
from flask import Blueprint, redirect, render_template, send_file, url_for

from roomQr import ROOMS


cages_bp = Blueprint("cages", __name__)


def all_cages():
    cages = []
    for room in ROOMS.values():
        for cage in room["cages"]:
            cage_record = cage.copy()
            cage_record.update(
                {
                    "room_id": room["id"],
                    "room_name": room["name"],
                    "room_number": room["room_number"],
                    "facility": room["facility"],
                    "department": room["department"],
                    "city": room["city"],
                    "principal_investigator": room["principal_investigator"],
                    "strain": room["strain"],
                }
            )
            cages.append(cage_record)
    return cages


def cage_by_id(cage_id):
    return next((cage for cage in all_cages() if cage["id"] == cage_id), None)


@cages_bp.route("/cages")
def cages():
    return render_template("cages/cages.html", cages=all_cages())


@cages_bp.route("/cages/<cage_id>")
def cage_detail(cage_id):
    cage = cage_by_id(cage_id)
    if cage is None:
        return redirect(url_for("cages.cages"))
    return render_template("cages/cage_detail.html", cage=cage)


@cages_bp.route("/cages/<cage_id>/qr.png")
def cage_qr(cage_id):
    cage = cage_by_id(cage_id)
    if cage is None:
        return "Cage not found", 404

    target_url = url_for("cages.cage_detail", cage_id=cage_id, _external=True)
    image = qrcode.make(target_url)
    image_io = BytesIO()
    image.save(image_io, "PNG")
    image_io.seek(0)
    return send_file(image_io, mimetype="image/png")


@cages_bp.route("/cages/<cage_id>/card")
def cage_card(cage_id):
    cage = cage_by_id(cage_id)
    if cage is None:
        return redirect(url_for("cages.cages"))

    return render_template(
        "cages/cage_card.html",
        cage=cage,
        qr_url=url_for("cages.cage_qr", cage_id=cage_id),
        detail_url=url_for("cages.cage_detail", cage_id=cage_id, _external=True),
    )
