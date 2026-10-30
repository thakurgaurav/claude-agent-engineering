"""Optimize rental recommendations using evaluator feedback.

Author: Gaurav Thakur

Description:
Improves rental recommendations using semantic evaluator feedback.
"""

import json
from typing import Any

from anthropic import Anthropic

from workflow_engineering.domain.rental import (
    RentalProperty,
    RentalSearchIntent,
)
from workflow_engineering.generators.rental_recommendation_generator import (
    RentalRecommendationOutput,
)
from workflow_engineering.prompt_loader import load_prompt
from workflow_engineering.structured_output import call_structured_tool


class RentalRecommendationOptimizer:
    """Improve a rental recommendation using evaluator feedback."""

    def __init__(self, client: Anthropic) -> None:
        """Initialize the optimizer with an Anthropic client."""
        self._client = client

    def optimize(
        self,
        user_request: str,
        intent: RentalSearchIntent,
        candidates: list[RentalProperty],
        previous_recommendation: RentalRecommendationOutput,
        feedback: list[str],
    ) -> RentalRecommendationOutput:
        """Revise a recommendation using semantic evaluator feedback."""
        if not candidates:
            raise ValueError(
                "At least one rental candidate is required for optimization."
            )

        if not feedback:
            raise ValueError(
                "Evaluator feedback is required for optimization."
            )

        recommendation = call_structured_tool(
            client=self._client,
            system_prompt=load_prompt(
                "rental_recommendation_optimizer.txt"
            ),
            user_message=self._build_optimization_message(
                user_request,
                intent,
                candidates,
                previous_recommendation,
                feedback,
            ),
            tool_name="record_optimized_rental_recommendation",
            tool_description=(
                "Record the complete revised rental recommendation after "
                "applying evaluator feedback. The tool input must include "
                "recommended_property_id and reasoning."
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
                "Claude optimized to a property outside the candidate set: "
                f"{recommendation.recommended_property_id}"
            )

        return recommendation

    @staticmethod
    def _build_optimization_message(
        user_request: str,
        intent: RentalSearchIntent,
        candidates: list[RentalProperty],
        previous_recommendation: RentalRecommendationOutput,
        feedback: list[str],
    ) -> str:
        """Build the evidence package used for recommendation optimization."""
        payload: dict[str, Any] = {
            "original_request": user_request,
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
            "previous_recommendation": {
                "recommended_property_id": (
                    previous_recommendation.recommended_property_id
                ),
                "reasoning": previous_recommendation.reasoning,
                "tradeoffs": previous_recommendation.tradeoffs,
            },
            "evaluator_feedback": feedback,
        }

        return json.dumps(payload, indent=2)
