"""
Physical Location Models.

This module defines the physical hierarchy of the LabSmartTrack app,
including Facilities, Rooms, Racks, and Cages.
"""

from database import db

#-- 1. LOCATION ---
class Location(db.Model):
    """
    Location model represents a physical location where
    mice are housed and bred.

    """
    __tablename__ = 'locations'

    location_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationships: A location can have many facilities.
    facilities = db.relationship('Facility', back_populates='location')

    def to_dict(self):
        """Convert the Location object to a dictionary."""
        return {
            'id': self.location_id,
            'name': self.name
        }

    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}')>"

# --- 2. FACILITY ---
class Facility(db.Model):
    """
    Facility model represents a research facility where
    mice are housed and bred.

    """
    __tablename__ = 'facilities'

    facility_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Foreign key: Looks up the location_id in the locations table.
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'),
                             nullable=False)

    # Relationship: A facility belongs to a location.
    location = db.relationship('Location', back_populates='facilities')

    # Relationships: A falicity can have many rooms.
    rooms = db.relationship('Room', back_populates='facility')

    def to_dict(self):
        """Convert the Facility object to a dictionary."""
        return {
            'id': self.facility_id,
            'name': self.name,
            'location_id': self.location_id
        }

    def __repr__(self):
        return f"<Facility(id={self.id}, name='{self.name}')>"

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
    racks = db.relationship('Rack', back_populates='room')

    def to_dict(self):
        """Convert the Room object to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'facility_id': self.facility_id
        }
    def __repr__(self):
        return f"<Room(id={self.id}, name='{self.name}')>"
      
# -- 4. RACK ---
class Rack(db.Model):
    """
    Rack model represents a rack within a room where
    mice are housed and bred.

    """
    __tablename__ = 'racks'

    rack_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Foreign key: Looks up the room_id in the rooms table.
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'),
                             nullable=False)
    # Relationship: A rack belongs to a room.
    room = db.relationship('Room', back_populates='racks')
    # Relationships: A rack can have many cages.
    cages = db.relationship('Cage', back_populates='rack')

    def to_dict(self):
        """Convert the Rack object to a dictionary."""
        return {
            'id': self.rack_id,
            'name': self.name,
            'room_id': self.room_id
        }

    def __repr__(self):
        return f"<Rack(id={self.rack_id}, name='{self.name}')>"

# --- 5. CAGE ---
class Cage(db.Model):
    """
    Cage model represents a cage within a rack where
    mice are housed and bred.
    """
    __tablename__ = 'cages'

    cage_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Foreign key: Looks up the rack_id in the racks table.
    rack_id = db.Column(db.Integer, db.ForeignKey('racks.id'), nullable=False)
    
    # Relationship: A cage belongs to a rack.
    rack = db.relationship('Rack', back_populates='cages')
    
    # Relationship: A cage can have many mice. 
    mice = db.relationship('Mouse', back_populates='cage')
    breeding_pairs = db.relationship('BreedingPair', back_populates='cage')

    def to_dict(self):
        """Convert the Cage object to a dictionary."""
        return {
            'id': self.cage_id,
            'name': self.name,
            'rack_id': self.rack_id
        }

    def __repr__(self):
        return f"<Cage(id={self.cage_id}, name='{self.name}')>"