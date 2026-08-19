from enum import Enum


class CageType(Enum):
    HOLDING = "Holding"
    MATING = "Mating"
    WEANING = "Weaning"
    EXPERIMENTAL = "Experimental"
    QUARANTINE = "Quarantine"


class CageStatus(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    HIDDEN = "Hidden"
    RETIRED = "Retired"
    NEEDS_ATTENTION = "Needs attention"


class MouseSex(Enum):
    MALE = "Male"
    FEMALE = "Female"
    UNKNOWN = "Unknown"


class MouseStatus(Enum):
    AVAILABLE = "Available"
    BREEDING = "Breeding"
    PREGNANT = "Pregnant"
    WITH_PUPS = "With pups"
    WEANED = "Weaned"
    RETIRED = "Retired"
    DECEASED = "Deceased"


class RoomCheckStatus(Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    REVIEWED = "Reviewed"
    NEEDS_CORRECTION = "Needs correction"