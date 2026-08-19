from flask_sqlalchemy import SQLAlchemy

import os
import sys
from labsmarttrack_enums import MouseStatus, MouseSex

db = SQLAlchemy()

#-- 1. LOCATION ---
class Location(db.Model):
    """
    Location model represents a physical location where
    mice are housed and bred.

    """
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationships: A location can have many facilities.
    facilities = db.relationship('Facility', back_populates='location',
                                 cascade='all, delete-orphan')

# --- 2. FACILITY ---
class Facility(db.Model):
    """
    Facility model represents a research facility where
    mice are housed and bred.

    """
    __tablename__ = 'facilities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Foreign key: Looks up the location_id in the locations table.
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'),
                             nullable=False)

    # Relationship: A facility belongs to a location.
    location = db.relationship('Location', back_populates='facilities')

    # Relationships: A falicity can have many rooms.
    rooms = db.relationship('Room', back_populates='facility',
                            cascade='all, delete-orphan')

# --- 3. ROOM ---
class Room(db.Model):
    """
    Room model represents a room within a facility where
    mice are housed and bred.

    """
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Foreign key: Looks up the facility_id in the facilities table.
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'),
                             nullable=False)

    # Relationship: A room belongs to a facility.
    facility = db.relationship('Facility', back_populates='rooms')
    # Relationships: A room can have many racks.
    racks = db.relationship('Rack', back_populates='room',
                            cascade='all, delete-orphan')
      
# -- 4. RACK ---
class Rack(db.Model):
    """
    Rack model represents a rack within a room where
    mice are housed and bred.

    """
    __tablename__ = 'racks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Foreign key: Looks up the room_id in the rooms table.
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'),
                             nullable=False)
    # Relationship: A rack belongs to a room.
    room = db.relationship('Room', back_populates='racks')
    # Relationships: A rack can have many cages.
    cages = db.relationship('Cage', back_populates='rack',
                            cascade='all, delete-orphan')

# --- 5. CAGE ---
class Cage(db.Model):
    """
    Cage model represents a cage within a rack where
    mice are housed and bred.
    """
    __tablename__ = 'cages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Foreign key: Looks up the rack_id in the racks table.
    rack_id = db.Column(db.Integer, db.ForeignKey('racks.id'), nullable=False)
    
    # Relationship: A cage belongs to a rack.
    rack = db.relationship('Rack', back_populates='cages')
    
    # Relationship: A cage can have many mice. 
    # NOTE: Removed 'cascade=all, delete-orphan' to protect your mouse records!
    mice = db.relationship('Mouse', back_populates='cage')


# --- 6. MOUSE ---
class Mouse(db.Model):
    """
    Mouse model represents a mouse within a cage.
    """
    __tablename__ = 'mice'

    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=True)
    strain = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.Enum(MouseSex), nullable=False, default=MouseSex.UNKNOWN)
    PI = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Enum(MouseStatus), nullable=True)
    is_hidden = db.Column(db.Boolean, default=False)
    genotype = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    death_date = db.Column(db.Date, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    protocol_id = db.Column(db.Integer, nullable=True)

    # Foreign Keys (Defined exactly once)
    cage_id = db.Column(db.Integer, db.ForeignKey('cages.id'), nullable=True)
    litter_id = db.Column(db.Integer, db.ForeignKey('litters.id'), nullable=True)

    # Relationships
    litter = db.relationship('Litter', back_populates='mice')
    cage = db.relationship('Cage', back_populates='mice')

    def to_dict(self):
        """Return a dictionary representation of the mouse and its hierarchy."""
        cage = self.cage
        rack = cage.rack if cage else None
        room = rack.room if rack else None
        facility = room.facility if room else None
        location = facility.location if facility else None
        gender_value = self.gender.value if isinstance(self.gender, MouseSex) else self.gender
        status_value = self.status.value if isinstance(self.status, MouseStatus) else self.status

        return {
            'id': self.id,
            'mouse_id': self.id,
            'age': self.age,
            'gender': gender_value,
            'strain': self.strain,
            'litter_id': self.litter_id,
            'litter_name': self.litter.name if self.litter and hasattr(self.litter, 'name') else None,
            'cage_id': cage.id if cage else None,
            'cage_name': cage.name if cage else None,
            'rack_id': rack.id if rack else None,
            'rack_name': rack.name if rack else None,
            'room_id': room.id if room else None,
            'room_name': room.name if room else None,
            'facility_id': facility.id if facility else None,
            'facility_name': facility.name if facility else None,
            'location_id': location.id if location else None,
            'location_name': location.name if location else None,
            'status': status_value,
            'is_hidden': self.is_hidden,
            'genotype': self.genotype,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'death_date': self.death_date.isoformat() if self.death_date else None,
            'weight': self.weight,
            'notes': self.notes,
            'protocol_id': self.protocol_id,
        }

    def __lt__(self, other):
        if not isinstance(other, Mouse):
            return NotImplemented
        left = (self.strain or '', self.id or 0)
        right = (other.strain or '', other.id or 0)
        return left < right

    def __repr__(self):
        return f"<Mouse id={self.id} strain={self.strain!r} cage_id={self.cage_id}>"