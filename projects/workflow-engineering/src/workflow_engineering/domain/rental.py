"""Domain models for the rental property selection workflow.

Author:
    Gaurav Thakur
Description:
    Defines rental search criteria, property evidence, and preference models.
"""

from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True)
class RentalSearchCriteria:
    """Hard constraints used to retrieve elibigle rental properties."""
    
    city: str
    max_monthly_rent: int | None = None
    min_bedrooms: int | None = None
    min_bathrooms: int | None = None
    pets_required: bool = False
    parking_required: bool = False
    property_type: str | None = None
    
    
    
@dataclass(frozen=True)
class RentalProperty:
    """Rental property evidence used by the selection workflow."""

    property_id: str
    city: str
    state: str
    zip_code: str
    neighborhood: str
    property_type: str
    bedrooms: int
    bathrooms: float
    square_feet: int
    year_built: int
    monthly_rent: int
    security_deposit: int
    lease_term_months: int
    available_from: str
    parking: bool
    pets_allowed: bool
    furnished: bool
    in_unit_laundry: bool
    gym: bool
    pool: bool
    air_conditioning: bool
    transit_score: float
    walkability_score: float
    school_rating: float
    safety_score: float
    
class PreferencePriority(StrEnum):
    """Importance levels for a renter's soft preferences."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    
class RentalPreferenceAttribute(StrEnum):
    """Supported semantic attributes for rental property preferences."""

    SAFETY = "safety"
    SPACE = "space"
    NEWNESS = "newness"
    WALKABILITY = "walkability"
    SCHOOLS = "schools"
    TRANSIT = "transit"
    IN_UNIT_LAUNDRY = "in_unit_laundry"
    GYM = "gym"
    POOL = "pool"
    AIR_CONDITIONING = "air_conditioning"
    FURNISHED = "furnished"
    

@dataclass(frozen=True)
class RentalPreference:
    """A renter's soft preference interpreted from natural language."""

    attribute: RentalPreferenceAttribute
    priority: PreferencePriority
    description: str
    
@dataclass(frozen=True)
class RentalSearchIntent:
    """Structured interpretation of a renter's natural-language request."""

    criteria: RentalSearchCriteria
    preferences: tuple[RentalPreference, ...]
    unsupported_requirements: tuple[str, ...] = ()
    
