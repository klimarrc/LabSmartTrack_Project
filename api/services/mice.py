
from labsmarttrack_enums import MouseStatus, MouseSex


class Mouse:

    def __init__(
        self,
        id,
        age=None,
        strain=None,
        gender=MouseSex.UNKNOWN,
        PI=None,
        cage_id=None,
        status=None,
        is_hidden=False,
        genotype=None,
        birth_date=None,
        death_date=None,
        weight=None,
        notes=None,
        protocol_id=None,
    ):
        self.id = id
        self.age = age
        self.strain = strain
        self.gender = gender
        self.PI = PI
        self.cage_id = cage_id
        self.status = status
        self.is_hidden = is_hidden
        self.genotype = genotype
        self.birth_date = birth_date
        self.death_date = death_date
        self.weight = weight
        self.notes = notes
        self.protocol_id = protocol_id

    def create_mouse(
        self,
        id,
        age,
        strain,
        gender=MouseSex.UNKNOWN,
        PI,
        cage_id,
        status,
        is_hidden=False,
        genotype=None,
        birth_date=None,
        death_date=None,
        weight=None,
        notes=None,
        protocol_id=None,
    ):
        return Mouse(
            id,
            age,
            strain,
            gender,
            PI,
            cage_id,
            status,
            is_hidden,
            genotype,
            birth_date,
            death_date,
            weight,
            notes,
            protocol_id,
        )