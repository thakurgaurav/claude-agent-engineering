"""Evidence mapping for supported rental property preferences.

Maps semantic rental concepts to fields available in the rental property
dataset.

Author: Gaurav Thakur

Description:
Maps rental preference concepts to measurable property evidence fields.
"""

from dataclasses import dataclass

from workflow_engineering.domain.rental import RentalPreferenceAttribute


@dataclass(frozen=True)
class RentalEvidenceDefinition:
    """Describe the dataset evidence supporting a rental preference."""

    field_name: str
    description: str


RENTAL_EVIDENCE: dict[
    RentalPreferenceAttribute,
    RentalEvidenceDefinition,
] = {
    RentalPreferenceAttribute.SAFETY: RentalEvidenceDefinition(
        field_name="safety_score",
        description="Safety score from 0 to 10; higher is better.",
    ),
    RentalPreferenceAttribute.SPACE: RentalEvidenceDefinition(
        field_name="square_feet",
        description="Property size measured in square feet.",
    ),
    RentalPreferenceAttribute.NEWNESS: RentalEvidenceDefinition(
        field_name="year_built",
        description="Year the property was built; later years indicate newer properties.",
    ),
    RentalPreferenceAttribute.WALKABILITY: RentalEvidenceDefinition(
        field_name="walkability_score",
        description="Walkability score from 0 to 100; higher is better.",
    ),
    RentalPreferenceAttribute.SCHOOLS: RentalEvidenceDefinition(
        field_name="school_rating",
        description="School rating associated with the property location.",
    ),
    RentalPreferenceAttribute.TRANSIT: RentalEvidenceDefinition(
        field_name="transit_score",
        description="Transit score associated with the property location.",
    ),
    RentalPreferenceAttribute.IN_UNIT_LAUNDRY: RentalEvidenceDefinition(
        field_name="in_unit_laundry",
        description="Whether the property provides in-unit laundry.",
    ),
    RentalPreferenceAttribute.GYM: RentalEvidenceDefinition(
        field_name="gym",
        description="Whether the property provides a gym.",
    ),
    RentalPreferenceAttribute.POOL: RentalEvidenceDefinition(
        field_name="pool",
        description="Whether the property provides a pool.",
    ),
    RentalPreferenceAttribute.AIR_CONDITIONING: RentalEvidenceDefinition(
        field_name="air_conditioning",
        description="Whether the property provides air conditioning.",
    ),
    RentalPreferenceAttribute.FURNISHED: RentalEvidenceDefinition(
        field_name="furnished",
        description="Whether the property is furnished.",
    ),
}
