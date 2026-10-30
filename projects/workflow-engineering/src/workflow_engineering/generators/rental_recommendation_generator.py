"""Generate an initial rental property recommendation using Claude.

Author: Gaurav Thakur

Description:
Generates evidence-based rental recommendations from eligible candidates.
"""

import json
from typing import Any

from anthropic import Anthropic
from pydantic import BaseModel, Field

from workflow_engineering.domain.rental import (
    RentalProperty,
    RentalSearchIntent,
)
from workflow_engineering.prompt_loader import load_prompt
from workflow_engineering.structured_output import call_structured_tool


class RentalRecommendationOutput(BaseModel):
    """Structured recommendation produced by Claude."""

    recommended_property_id: str = Field(
        ...,
        min_length=1,
        description=(
            "Property ID of the single rental property selected from "
            "the provided candidate set."
        ),
    )

    reasoning: str = Field(
        ...,
        min_length=1,
        description=(
            "Evidence-based explanation of why the selected property "
            "provides the best overall balance for the user's stated "
            "preferences."
        ),
    )

    tradeoffs: list[str] = Field(
        default_factory=list,
        description=(
            "Optional structured summary of important gains or losses "
            "relative to other strong candidates."
        ),
    )


class RentalRecommendationGenerator:
    """Generate a rental recommendation from eligible candidate properties."""

    def __init__(self, client: Anthropic) -> None:
        """Initialize the generator with an Anthropic client."""
        self._client = client

    def generate(
        self,
        user_request: str,
        intent: RentalSearchIntent,
        candidates: list[RentalProperty],
    ) -> RentalRecommendationOutput:
        """Generate an initial recommendation from eligible candidates."""
        if not candidates:
            raise ValueError(
                "At least one rental candidate is required."
            )

        recommendation = call_structured_tool(
            client=self._client,
            system_prompt=load_prompt(
                "rental_recommendation_generator.txt"
            ),
            user_message=self._build_user_message(
                user_request,
                intent,
                candidates,
            ),
            tool_name="record_rental_recommendation",
            tool_description=(
                "Select exactly one property from the provided candidate "
                "set and record the complete recommendation. The tool input "
                "must include recommended_property_id and reasoning."
            ),
            output_model=RentalRecommendationOutput,
            max_tokens=2000,
        )

        candidate_ids = {
            candidate.property_id
            for candidate in candidates
        }

        if recommendation.recommended_property_id not in candidate_ids:
            raise RuntimeError(
                "Claude recommended a property outside the candidate set: "
                f"{recommendation.recommended_property_id}"
            )

        return recommendation

    @staticmethod
    def _build_user_message(
        user_request: str,
        intent: RentalSearchIntent,
        candidates: list[RentalProperty],
    ) -> str:
        """Build the evidence package provided to Claude."""
        payload: dict[str, Any] = {
            "original_request": user_request,
            "interpreted_intent": {
                "hard_constraints": {
                    "city": intent.criteria.city,
                    "max_monthly_rent": (
                        intent.criteria.max_monthly_rent
                    ),
                    "min_bedrooms": intent.criteria.min_bedrooms,
                    "min_bathrooms": intent.criteria.min_bathrooms,
                    "pets_required": intent.criteria.pets_required,
                    "parking_required": intent.criteria.parking_required,
                    "property_type": intent.criteria.property_type,
                },
                "preferences": [
                    {
                        "attribute": preference.attribute.value,
                        "priority": preference.priority.value,
                        "description": preference.description,
                    }
                    for preference in intent.preferences
                ],
                "unsupported_requirements": list(
                    intent.unsupported_requirements
                ),
            },
            "candidate_properties": [
                {
                    "property_id": candidate.property_id,
                    "monthly_rent": candidate.monthly_rent,
                    "bedrooms": candidate.bedrooms,
                    "bathrooms": candidate.bathrooms,
                    "square_feet": candidate.square_feet,
                    "year_built": candidate.year_built,
                    "parking": candidate.parking,
                    "pets_allowed": candidate.pets_allowed,
                    "furnished": candidate.furnished,
                    "in_unit_laundry": candidate.in_unit_laundry,
                    "gym": candidate.gym,
                    "pool": candidate.pool,
                    "air_conditioning": candidate.air_conditioning,
                    "transit_score": candidate.transit_score,
                    "walkability_score": candidate.walkability_score,
                    "school_rating": candidate.school_rating,
                    "safety_score": candidate.safety_score,
                }
                for candidate in candidates
            ],
        }

        return json.dumps(payload, indent=2)
