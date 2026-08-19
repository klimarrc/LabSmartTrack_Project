"""
Biological and Mouse Models.

This module defines the living entities in the LabSmartTrack app,
including Strains, Litters, and individual Mice.
"""

from database import db

from labsmarttrack_enums import MouseStatus, MouseSex



# --- Mouse Model ---
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
        """Convert the Mouse object to a dictionary."""
        return {
            'id': self.id,
            'age': self.age,
            'strain': self.strain,
            'gender': self.gender.value if isinstance(self.gender, MouseSex) else self.gender,
            'PI': self.PI,
            'status': self.status.value if isinstance(self.status, MouseStatus) else self.status,
            'is_hidden': self.is_hidden,
            'genotype': self.genotype,
            'dob': self.birth_date.isoformat() if self.birth_date else None,
            'death_date': self.death_date.isoformat() if self.death_date else None,
            'weight': self.weight,
            'notes': self.notes,
            'protocol_id': self.protocol_id
        }

    def __lt__(self, other):
        """Define less-than comparison based on mouse ID."""
        if not isinstance(other, Mouse):
            return NotImplemented
        return self.id < other.id

    def __repr__(self):
        """Define the string representation of the Mouse object."""
        return (
            f"<Mouse(id={self.id}, strain={self.strain},"
            f"gender={self.gender}, status={self.status})"
            f"dob={self.birth_date}, cage_id={self.cage_id})>"

        )