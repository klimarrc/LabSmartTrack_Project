from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(40), nullable=False, default="staff")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    room_code = db.Column(db.String(40), unique=True, nullable=False)
    building = db.Column(db.String(120))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    racks = db.relationship("Rack", backref="room", lazy=True)
    room_checks = db.relationship("RoomCheck", backref="room", lazy=True)


class Rack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)
    rack_code = db.Column(db.String(80), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    cages = db.relationship("Cage", backref="rack", lazy=True)


class Cage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rack_id = db.Column(db.Integer, db.ForeignKey("rack.id"), nullable=True)
    cage_code = db.Column(db.String(80), unique=True, nullable=False)
    status = db.Column(db.String(40), nullable=False, default="active")
    max_capacity = db.Column(db.Integer, nullable=False, default=5)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    mice = db.relationship("Mouse", backref="cage", lazy=True)
    cage_events = db.relationship("CageEvent", backref="cage", lazy=True)


class Strain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)

    mice = db.relationship("Mouse", backref="strain", lazy=True)


class Mouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mouse_code = db.Column(db.String(80), unique=True, nullable=False)
    cage_id = db.Column(db.Integer, db.ForeignKey("cage.id"), nullable=True)
    strain_id = db.Column(db.Integer, db.ForeignKey("strain.id"), nullable=True)
    sex = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date)
    status = db.Column(db.String(40), nullable=False, default="active")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    genotypes = db.relationship("Genotype", backref="mouse", lazy=True)
    mouse_events = db.relationship("MouseEvent", backref="mouse", lazy=True)


class Genotype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mouse_id = db.Column(db.Integer, db.ForeignKey("mouse.id"), nullable=False)
    marker = db.Column(db.String(120), nullable=False)
    result = db.Column(db.String(120), nullable=False)
    tested_at = db.Column(db.Date)
    notes = db.Column(db.Text)


class BreedingPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    breeding_code = db.Column(db.String(80), unique=True, nullable=False)
    sire_id = db.Column(db.Integer, db.ForeignKey("mouse.id"), nullable=True)
    dam_id = db.Column(db.Integer, db.ForeignKey("mouse.id"), nullable=True)
    cage_id = db.Column(db.Integer, db.ForeignKey("cage.id"), nullable=True)
    status = db.Column(db.String(40), nullable=False, default="active")
    start_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    litters = db.relationship("Litter", backref="breeding_pair", lazy=True)


class Litter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    litter_code = db.Column(db.String(80), unique=True, nullable=False)
    breeding_pair_id = db.Column(db.Integer, db.ForeignKey("breeding_pair.id"), nullable=False)
    born_date = db.Column(db.Date)
    wean_due_date = db.Column(db.Date)
    pup_count = db.Column(db.Integer, nullable=False, default=0)
    notes = db.Column(db.Text)


class RoomCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    status = db.Column(db.String(40), nullable=False, default="submitted")
    food_checked = db.Column(db.Boolean, nullable=False, default=False)
    water_checked = db.Column(db.Boolean, nullable=False, default=False)
    health_checked = db.Column(db.Boolean, nullable=False, default=False)
    environment_checked = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class CageEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cage_id = db.Column(db.Integer, db.ForeignKey("cage.id"), nullable=False)
    event_type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class MouseEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mouse_id = db.Column(db.Integer, db.ForeignKey("mouse.id"), nullable=False)
    event_type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    action = db.Column(db.String(120), nullable=False)
    table_name = db.Column(db.String(120))
    record_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
