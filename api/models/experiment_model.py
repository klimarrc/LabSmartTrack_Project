"""
Experiment and Protocol Models.

This module defines the scientific studies and ethical protocols 
associated with the mice in the LabSmartTrack app.
"""

from database import db

# --- 1. Protocol ---
class Protocol(db.Model):
    """
    Protocol model represents an approved IACUC/ethics protocol.
    """
    __tablename__ = 'protocols'

    id = db.Column(db.Integer, primary_key=True)
    protocol_number = db.Column(db.String(100), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=True)
    principal_investigator = db.Column(db.String(100), nullable=True)
    approval_date = db.Column(db.Date, nullable=True)
    expiration_date = db.Column(db.Date, nullable=True)

    # Relationships: A protocol can have many experiments
    experiments = db.relationship('Experiment', back_populates='protocol')
    
    # Relationships: A protocol can have many mice
    mice = db.relationship('Mouse', back_populates='protocol')

    def to_dict(self):
        return {
            'id': self.id,
            'protocol_number': self.protocol_number,
            'title': self.title,
            'principal_investigator': self.principal_investigator,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None
        }

    def __repr__(self):
        return f"<Protocol(number='{self.protocol_number}')>"


# --- 2. Experiment ---
class Experiment(db.Model):
    """
    Experiment model represents a specific scientific study.
    """
    __tablename__ = 'experiments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    researcher_name = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='planned') # planned, active, completed

    # Foreign Key connecting to the Protocol
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocols.id'), nullable=True)

    # Relationships
    protocol = db.relationship('Protocol', back_populates='experiments')
    
    # Relationships: An experiment can have many mice assigned to it
    mice = db.relationship('Mouse', back_populates='experiment')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'researcher_name': self.researcher_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'protocol_id': self.protocol_id
        }

    def __repr__(self):
        return f"<Experiment(name='{self.name}', status='{self.status}')>"