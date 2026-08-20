"""
This script is used to seed the database with initial data for testing 
and development purposes.
It creates facilities, rooms, racks, cages, strains, mice, and breeding pairs.
"""
from datetime import date
from app import create_app
from database import db

# Import data.room_data to ensure ROOMS is available for seeding
from data.room_data import ROOMS

# Import all your models and enums
from blueprints.room_qr import room_qr_bp
from api.models.location_model import Facility, Room, Rack, Cage
from api.models.breeding_model import Strain, BreedingPair
from api.models.mouse_model import Mouse
from labsmarttrack_enums import MouseSex


def seed_database():
    """Seeds the database with initial data."""
    app = create_app()
    with app.app_context():
        print("🗑️  Clearing old database tables...")
        db.drop_all()
        print("🏗️  Creating fresh tables...")
        db.create_all()

        print("🌱 Seeding Facilities and Rooms...")
        fac1 = Facility(name="Main Research Center")
        fac2 = Facility(name="North Wing Annex")
        db.session.add_all([fac1, fac2])
        db.session.commit()

        print("🌱 Seeding Rooms...")
        room1 = Room(name="Room 101", facility_id=fac1.id)
        room2 = Room(name="Room 102", facility_id=fac1.id)
        room3 = Room(name="Room A", facility_id=fac2.id)
        db.session.add_all([room1, room2, room3])
        db.session.commit()

        print("🌱 Seeding Racks and Cages...")
        rack1 = Rack(name="Rack 1", room_id=room1.id)
        db.session.add(rack1)
        db.session.commit()

        # Create 3 cages
        cage1 = Cage(cage_card_number="C-001", rack_id=rack1.id)
        cage2 = Cage(cage_card_number="C-002", rack_id=rack1.id)
        cage3 = Cage(cage_card_number="C-003", rack_id=rack1.id)
        db.session.add_all([cage1, cage2, cage3])
        db.session.commit()

        print("🌱 Seeding Strains and Mice...")
        strain1 = Strain(name="C57BL/6", background="Black")
        db.session.add(strain1)
        db.session.commit()

        # Create Male and Female mice
        sire = Mouse(
            rfid_tag="RFID-M001", 
            gender=MouseSex.MALE, 
            status="active",
            dob=date(2025, 1, 15),
            cage_id=cage1.id,
            strain_id=strain1.id
        )
        dam = Mouse(
            rfid_tag="RFID-F001",
            gender=MouseSex.FEMALE,
            status="active",
            dob=date(2025, 1, 20),
            cage_id=cage1.id,
            strain_id=strain1.id
        )
        dam2 = Mouse(
            rfid_tag="RFID-F002", 
            gender=MouseSex.FEMALE,
            status="active",
            dob=date(2025, 2, 10),
            cage_id=cage2.id,
            strain_id=strain1.id
        )
        db.session.add_all([sire, dam, dam2])
        db.session.commit()

        print("🌱 Seeding Breeding Pairs...")
        pair1 = BreedingPair(
            breeding_code="BP-2026-001",
            principal_investigator="Dr. Smith",
            strain_name="C57BL/6",
            mating_type="Pair: 1 male + 1 female",
            sire_id=sire.id,
            dam_id=dam.id,
            cage_id=cage1.id,
            status="active",
            start_date=date(2026, 8, 1)
        )
        db.session.add(pair1)
        db.session.commit()

        print("✅ Database successfully seeded! You are ready to build the UI.")

if __name__ == "__main__":
    seed_database()