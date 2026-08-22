from app.services.breeding_service import BreedingService
from app import app
from api.models import db
import unittest


class FakeMouse:
    def __init__(self, id):
        self.id = id


class FakeCage:
    def __init__(self, id):
        self.id = id


with app.app_context():
    db.create_all()

    service = BreedingService()

    sire = FakeMouse(id=1)
    dam = FakeMouse(id=2)
    cage = FakeCage(id=1)

    pair = service.create_breeding_pair(
        breeding_code="BP-001",
        sire=sire,
        dam=dam,
        cage=cage,
        principal_investigator="Dr. Chen",
        strain_name="C57BL/6J",
    )

    litter = service.create_litter(
        breeding_pair=pair,
        litter_code="L-001",
        pup_count=8,
    )

    print(pair.breeding_code)
    print(litter.litter_code)
    print(litter.wean_due_date)