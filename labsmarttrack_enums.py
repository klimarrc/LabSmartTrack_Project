"""
LabSmartTrack Enums
This module defines the enumerations used in the LabSmartTrack app,
including CageType, CageStatus, MouseSex, and MouseStatus.
"""

from enum import Enum


class CageType(Enum):
    """Types of cages in the facility."""
    
    HOLDING = "Holding"
    MATING = "Mating"
    WEANING = "Weaning"
    EXPERIMENTAL = "Experimental"
    QUARANTINE = "Quarantine"


class CageStatus(Enum):
    """Lifecycle status of a cage in the facility."""

    ACTIVE = "Active"
    INACTIVE = "Inactive"
    HIDDEN = "Hidden"
    RETIRED = "Retired"
    NEEDS_ATTENTION = "Needs attention"


class MouseSex(Enum):
    """Sex of a mouse."""

    MALE = "Male"
    FEMALE = "Female"
    UNKNOWN = "Unknown"


class MouseStatus(Enum):
    """Lifecycle status of a mouse in the facility."""
    AVAILABLE = "Available"
    BREEDING = "Breeding"
    PREGNANT = "Pregnant"
    WITH_PUPS = "With pups"
    WEANED = "Weaned"
    RETIRED = "Retired"
    DECEASED = "Deceased"
    
