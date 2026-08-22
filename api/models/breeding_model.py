"""Base class for biological models in the LabSmartTrack app."""

from database import db

# --- 1. BreedingPair ---
class BreedingPair(db.Model):
    """
    BreedingPair model represents a pair of mice used for breeding.
    """
    __tablename__ = 'breeding_pairs'

    id = db.Column(db.Integer, primary_key=True)
    breeding_code = db.Column(db.String(100),unique=True, nullable=False)
    principal_investigator = db.Column(db.String(100), nullable=True)
    strain_name = db.Column(db.String(100), nullable=True)
    mating_type = db.Column(db.String(100), nullable=True)

    # Foreign Keys connecting to the Mouse model
    # (Assuming your Mouse model uses 'id' as its primary key. If it uses 
    # 'mouse_id', change these to 'mice.mouse_id')
    sire_id = db.Column(db.Integer, db.ForeignKey('mice.id'), nullable=False)
    dam_id = db.Column(db.Integer, db.ForeignKey('mice.id'), nullable=False)
    dam2_id = db.Column(db.Integer, db.ForeignKey('mice.id'), nullable=True)

    # Foreign Keys connecting to the Strain and Cage models
    strain_id = db.Column(db.Integer, db.ForeignKey('strains.id'), nullable=True)
    cage_id = db.Column(db.Integer, db.ForeignKey('cages.cage_id'), nullable=True)

    # Relationships
    strain = db.relationship('Strain', back_populates='breeding_pairs')
    cage = db.relationship('Cage', back_populates='breeding_pairs')

    sire = db.relationship('Mouse', foreign_keys=[sire_id], backref='sire_of')
    dam = db.relationship('Mouse', foreign_keys=[dam_id], backref='dam_of')
    dam2 = db.relationship('Mouse', foreign_keys=[dam2_id], backref='dam2_of')

    # Relationships: A breeding pair can have many litters.
    litters = db.relationship('Litter', back_populates='breeding_pair')
   

    def to_dict(self):
        """Convert the BreedingPair object to a dictionary."""
        return {
            'id': self.id,
            'breeding_code': self.breeding_code,
            'principal_investigator': self.principal_investigator,
            'mating_type': self.mating_type,
            'sire_id': self.sire_id,
            'dam_id': self.dam_id,
            'dam2_id': self.dam2_id,
            'cage_id': self.cage_id,
            'strain_id': self.strain_id
        }

    def __repr__(self):
        return f"<BreedingPair(code='{self.breeding_code}')>"

# --- 2. Strain ---
class Strain(db.Model):
    """
    Strain model represents a specific strain of mice in the facility.

    """
    __tablename__ = 'strains'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationships: A strain can have many mice.
    mice = db.relationship('Mouse', back_populates='strain')

    # Relationships: A strain can have many breeding pairs.
    breeding_pairs = db.relationship('BreedingPair', back_populates='strain')
    
    def to_dict(self):
        """Convert the Strain object to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    def __repr__(self):
        """ repr method for debugging and logging purposes. """
        return f"<Strain(id={self.id}, name='{self.name}')>"

# --- 3. Litter ---
class Litter(db.Model):
    """
    Litter model represents a litter of mice born from a breeding pair.

    """
    __tablename__ = 'litters'

    id = db.Column(db.Integer, primary_key=True)
    litter_code = db.Column(db.String(100), nullable=False, unique=True)
    born_date = db.Column(db.Date, nullable=False)
    pup_count = db.Column(db.Integer, nullable=False, default=0)
    wean_due_date = db.Column(db.Date, nullable=True)

    # Foreign Key connecting to the BreedingPair model
    breeding_pair_id = db.Column(db.Integer, db.ForeignKey('breeding_pairs.id'),
                                 nullable=False)

    # Relationships
    breeding_pair = db.relationship('BreedingPair', back_populates='litters')

    # Relationships: A litter can have many mice.
    mice = db.relationship('Mouse', back_populates='litter')

    def to_dict(self):
        """Convert the Litter object to a dictionary."""
        return {
            'id': self.id,
            'litter_code': self.litter_code,
            'born_date': self.born_date.isoformat() if self.born_date else None,
            'pup_count': self.pup_count,
            'wean_due_date': self.wean_due_date.isoformat() if self.wean_due_date else None,
            'breeding_pair_id': self.breeding_pair_id
        }

    def __lt__(self, other):
        """Sort litters by born_date (oldest first)."""
        if not isinstance(other, Litter):
            return NotImplemented
        if not self.born_date or not other.born_date:
            return self.id < other.id
        return self.born_date < other.born_date

    def __repr__(self):
        return f"<Litter(code='{self.litter_code}', pups={self.pup_count})>"