from datetime import date
from app import create_app
from database import db

# Import all your models and enums
from api.models.location_model import Facility, Room, Rack, Cage
from api.models.breeding_model import Strain, BreedingPair, Litter
from api.models.mouse_model import Mouse
from labsmarttrack_enums import MouseSex, MouseStatus

def seed_database():
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

        # Notice: Just fac1.facility_id (no .id in the middle!)
        room1 = Room(name="Room 101", facility_id=fac1.facility_id)
        room2 = Room(name="Room 102", facility_id=fac1.facility_id)
        room3 = Room(name="Room A", facility_id=fac2.facility_id)
        db.session.add_all([room1, room2, room3])
        db.session.commit()

        print("🌱 Seeding Racks and Cages...")
        rack1 = Rack(name="Rack 1", room_id=room1.room_id)
        db.session.add(rack1)
        db.session.commit()

        cage1 = Cage(name="C-001", rack_id=rack1.rack_id)
        cage2 = Cage(name="C-002", rack_id=rack1.rack_id)
        cage3 = Cage(name="C-003", rack_id=rack1.rack_id)
        db.session.add_all([cage1, cage2, cage3])
        db.session.commit()

        print("🌱 Seeding Strains and Mice...")
        strain1 = Strain(name="C57BL/6")
        db.session.add(strain1)
        db.session.commit()

        sire = Mouse(
            gender=MouseSex.MALE, 
            status=MouseStatus.ACTIVE,
            birth_date=date(2025, 1, 15),
            cage_id=cage1.cage_id,
            strain_id=strain1.id
        )
        dam = Mouse(
            gender=MouseSex.FEMALE, 
            status=MouseStatus.ACTIVE,
            birth_date=date(2025, 1, 20),
            cage_id=cage1.cage_id,
            strain_id=strain1.id
        )
        dam2 = Mouse(
            gender=MouseSex.FEMALE, 
            status=MouseStatus.ACTIVE,
            birth_date=date(2025, 2, 10),
            cage_id=cage2.cage_id,
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
            cage_id=cage1.cage_id
        )
        db.session.add(pair1)
        db.session.commit()

        print("✅ Database successfully seeded! You are ready to build the UI.")

if __name__ == "__main__":
    seed_database()