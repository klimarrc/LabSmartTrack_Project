from flask_sqlalchemy import SQLAlchemy

import os
import sys
import logging
from labsmarttrack_enums import *

db = SQLAlchemy()

# --- 1. FACILITY ---
class Facility(db.Model):
    """
    Facility model represents a research facility where 
    mice are housed and bred.
    
    """
    __tablename__ = 'facilities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Realationships: A falicity can have many rooms.
    rooms = db.relationship('Room', back_populates='facility', 
                            cascade='all, delete-orphan')
    def __repr__(self):
        return f"<Facility {self.name}>"
