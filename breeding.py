from datetime import datetime

from models import BreedingPair


class Breeding:
    
    def __init__(self, dam, sire):
        self.dam = dam
        self.sire = sire
    
    def create_breeding_pair(self):
        """
        Create a new breeding pair with the given dam and sire.

        arguments:
        dam -- The dam (female mouse) for the breeding pair.
        sire -- The sire (male mouse) for the breeding pair.

        returns:
        A new BreedingPair object representing the created breeding pair.
        raises:
        ValueError -- If either the dam or sire is not provided.

        example:
        dam = Mouse.query.get(dam_id)
        sire = Mouse.query.get(sire_id)
        breeding = Breeding(dam, sire)
        new_pair = breeding.create_breeding_pair()

        """
        if not self.dam or not self.sire:
            raise ValueError("Both dam and sire must be provided.")

        breeding_pair = BreedingPair(
            dam_id=self.dam.id,
            sire_id=self.sire.id,
            status="active",
            start_date=datetime.utcnow(),
        )
        db.session.add(breeding_pair)
        db.session.commit()
        return breeding_pair
    
    def create_litter(self, breeding_pair, litter_code):
        litter = Litter(
            litter_code=litter_code,
            breeding_pair_id=breeding_pair.id
        )
        db.session.add(litter)
        db.session.commit()
        return litter
    
    def get_breeding_pairs(self):
        return BreedingPair.query.all()
    
    def get_breeding_pair_by_id(self,pair_id):
        return BreedingPair.query.get(pair_id)

     
