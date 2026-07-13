from datetime import date, datetime, timedelta
from typing import Optional

from models import BreedingPair, Litter, db


class BreedingService:
    """Database operations for breeding pairs and litters."""

    def create_breeding_pair(
        self,
        breeding_code: str,
        dam,
        sire,
        cage=None,
        dam2=None,
        principal_investigator: str = "",
        strain_name: str = "",
        mating_type: str = "Pair: 1 male + 1 female",
        post_litter_male_plan: str = "Separate male after litter is born",
        start_date: Optional[date] = None,
    ) -> BreedingPair:
        if not breeding_code:
            raise ValueError("Breeding code is required.")
        if dam is None or sire is None:
            raise ValueError("Both dam and sire must be provided.")

        breeding_pair = BreedingPair(
            breeding_code=breeding_code,
            principal_investigator=principal_investigator,
            strain_name=strain_name,
            mating_type=mating_type,
            sire_id=sire.id,
            dam_id=dam.id,
            dam2_id=dam2.id if dam2 else None,
            cage_id=cage.id if cage else None,
            post_litter_male_plan=post_litter_male_plan,
            status="active",
            start_date=start_date or date.today(),
        )

        db.session.add(breeding_pair)
        db.session.commit()
        return breeding_pair

    def create_litter(
        self,
        breeding_pair: BreedingPair,
        litter_code: str,
        born_date: Optional[date] = None,
        pup_count: int = 0,
        wean_due_date: Optional[date] = None,
    ) -> Litter:
        if breeding_pair is None:
            raise ValueError("Breeding pair is required.")
        if not litter_code:
            raise ValueError("Litter code is required.")

        litter_born_date = born_date or date.today()
        litter = Litter(
            litter_code=litter_code,
            breeding_pair_id=breeding_pair.id,
            born_date=litter_born_date,
            wean_due_date=wean_due_date or litter_born_date + timedelta(days=21),
            pup_count=pup_count,
        )

        db.session.add(litter)
        db.session.commit()
        return litter

    def retire_breeding_pair(self, breeding_pair: BreedingPair) -> BreedingPair:
        if breeding_pair is None:
            raise ValueError("Breeding pair is required.")

        breeding_pair.status = "retired"
        db.session.commit()
        return breeding_pair

    def get_breeding_pairs(self):
        return BreedingPair.query.order_by(BreedingPair.start_date.desc()).all()

    def get_breeding_pair_by_id(self, pair_id: int):
        return BreedingPair.query.get(pair_id)

    def get_breeding_pair_by_code(self, breeding_code: str):
        return BreedingPair.query.filter_by(breeding_code=breeding_code).first()


    def parse_date(value: str) -> Optional[date]:
        if not value:
            return None
        return datetime.strptime(value, "%Y-%m-%d").date()
