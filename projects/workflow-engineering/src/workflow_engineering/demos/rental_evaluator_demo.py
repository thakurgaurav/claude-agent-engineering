"""Demonstrate semantic evaluation of a rental recommendation.

Author: Gaurav Thakur

Description:
Demonstrates semantic evaluation of a generated rental recommendation.
"""

from claude_engineering.claude_client import create_claude_client

from workflow_engineering.domain.rental import (
    PreferencePriority,
    RentalPreference,
    RentalPreferenceAttribute,
    RentalProperty,
    RentalSearchCriteria,
    RentalSearchIntent,
)
from workflow_engineering.evaluators.rental_recommendation_evaluator import (
    RentalRecommendationEvaluator,
)
from workflow_engineering.generators.rental_recommendation_generator import (
    RentalRecommendationOutput,
)

USER_REQUEST = """
I'm looking for a 2-bedroom apartment in San Jose.
My absolute maximum is $3,500.
I have a dog, so pets must be allowed, and I need parking.

Safety is extremely important. I'd prefer something newer and spacious,
but I'd happily take an older or slightly smaller apartment if it's
significantly safer.

In-unit laundry is important.
A gym is nice but doesn't really matter.
"""


def create_property(
    property_id: str,
    *,
    safety_score: float,
    square_feet: int,
    year_built: int,
    in_unit_laundry: bool,
    gym: bool,
) -> RentalProperty:
    """Create rental evidence for the evaluator demo."""
    return RentalProperty(
        property_id=property_id,
        city="San Jose",
        state="CA",
        zip_code="95112",
        neighborhood="Demo Neighborhood",
        property_type="Apartment",
        bedrooms=2,
        bathrooms=2.0,
        square_feet=square_feet,
        year_built=year_built,
        monthly_rent=3200,
        security_deposit=3200,
        lease_term_months=12,
        available_from="2026-11-01",
        parking=True,
        pets_allowed=True,
        furnished=False,
        in_unit_laundry=in_unit_laundry,
        gym=gym,
        pool=False,
        air_conditioning=True,
        transit_score=60.0,
        walkability_score=70.0,
        school_rating=7.0,
        safety_score=safety_score,
    )


def main() -> None:
    """Evaluate a deliberately weak rental recommendation."""
    intent = RentalSearchIntent(
        criteria=RentalSearchCriteria(
            city="San Jose",
            max_monthly_rent=3500,
            min_bedrooms=2,
            pets_required=True,
            parking_required=True,
            property_type="apartment",
        ),
        preferences=(
            RentalPreference(
                attribute=RentalPreferenceAttribute.SAFETY,
                priority=PreferencePriority.VERY_HIGH,
                description="Safety is extremely important.",
            ),
            RentalPreference(
                attribute=RentalPreferenceAttribute.IN_UNIT_LAUNDRY,
                priority=PreferencePriority.HIGH,
                description="In-unit laundry is important.",
            ),
            RentalPreference(
                attribute=RentalPreferenceAttribute.NEWNESS,
                priority=PreferencePriority.MEDIUM,
                description="A newer property is preferred.",
            ),
            RentalPreference(
                attribute=RentalPreferenceAttribute.SPACE,
                priority=PreferencePriority.MEDIUM,
                description="A spacious property is preferred.",
            ),
            RentalPreference(
                attribute=RentalPreferenceAttribute.GYM,
                priority=PreferencePriority.LOW,
                description="A gym is nice but not important.",
            ),
        ),
    )

    candidates = [
        create_property(
            "SAFE-001",
            safety_score=9.2,
            square_feet=1050,
            year_built=1995,
            in_unit_laundry=True,
            gym=False,
        ),
        create_property(
            "GYM-002",
            safety_score=5.8,
            square_feet=1200,
            year_built=2022,
            in_unit_laundry=True,
            gym=True,
        ),
    ]

    recommendation = RentalRecommendationOutput(
        recommended_property_id="GYM-002",
        reasoning=(
            "GYM-002 is newer, larger, and includes a gym, "
            "making it the better overall choice."
        ),
        tradeoffs=[
            "It has a lower safety score than SAFE-001.",
        ],
    )

    client = create_claude_client()
    evaluator = RentalRecommendationEvaluator(client)

    evaluation = evaluator.evaluate(
        USER_REQUEST,
        intent,
        candidates,
        recommendation,
    )

    print("\nEvaluator Result")
    print("================")
    print("Status:", evaluation.status.value)

    print("\nFeedback:")
    if evaluation.feedback:
        for feedback in evaluation.feedback:
            print(f"- {feedback}")
    else:
        print("- None")


if __name__ == "__main__":
    main()
