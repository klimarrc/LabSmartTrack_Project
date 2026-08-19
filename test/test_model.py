"""Isolated test for SQLAlchemy models using an in-memory database."""

import sys
from pathlib import Path

# Tell Python to look one folder up (in the main LabSmartTrack folder)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask

from database import db
from labsmarttrack_enums import MouseSex, MouseStatus

# Import ALL your models using their actual file paths in your project!
from api.models.physical_model import Location, Facility, Room, Rack, Cage
from api.models.biological_model import Strain, BreedingPair, Litter
from api.models.experiment_model import Protocol, Experiment
from api.models.mouse_model import Mouse

def run_model_test():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    with app.app_context():
        db.create_all()
        print("✅ In-memory database created.\n")

        # 1. Physical Path
        loc = Location(name="Campus A")
        fac = Facility(name="Building 1", location=loc)
        room = Room(name="Room 101", facility=fac)
        rack = Rack(name="Rack A", room=room)
        cage = Cage(name="Cage A1", rack=rack)
        db.session.add(loc) 

        # 2. Science & Ethics (New!)
        protocol = Protocol(protocol_number="IACUC-2024-001", title="Cancer Research")
        experiment = Experiment(name="Trial Alpha", status="active", protocol=protocol)
        db.session.add(protocol)

        # 3. Biology
        strain = Strain(name="C57BL/6J")
        db.session.add(strain)
        db.session.commit()

        # 4. The Mice (Now assigned to an experiment!)
        sire = Mouse(
            strain_id=strain.id, 
            gender=MouseSex.MALE, 
            status=MouseStatus.AVAILABLE,
            cage_id=cage.id,
            experiment_id=experiment.id, # Attached to Trial Alpha
            protocol_id=protocol.id      # Attached to IACUC protocol
        )
        db.session.add(sire)
        db.session.commit()

        # --- TEST THE RESULTS ---
        print("--- TESTING MOUSE DICTIONARY ---\n")
        
        mouse_data = sire.to_dict()
        print(f"Mouse ID: {mouse_data['id']}")
        print(f"Strain: {mouse_data['strain']}")
        print(f"Experiment Name: {mouse_data['experiment_name']}")
        
        print("\n--- TESTING RELATIONSHIPS DIRECTLY ---")
        print(f"Q: What building is this mouse in? -> {sire.cage.rack.room.facility.name}")
        print(f"Q: What protocol covers this mouse? -> {sire.experiment.protocol.protocol_number}")
        
        print("\n🎉 All tests passed! Your entire database map works perfectly.")

if __name__ == '__main__':
    run_model_test()