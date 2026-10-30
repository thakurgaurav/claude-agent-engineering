"""Evaluate rental recommendations using Claude semantic judgment.

Author: Gaurav Thakur

Description:
Evaluates rental recommendations against user requirements and preferences.
"""

import json
from enum import StrEnum
from typing import Any

from anthropic import Anthropic
from pydantic import BaseModel, Field, model_validator

from workflow_engineering.domain.rental import (
    RentalProperty,
    RentalSearchIntent,
)
from workflow_engineering.generators.rental_recommendation_generator import (
    RentalRecommendationOutput,
)
from workflow_engineering.prompt_loader import load_prompt
from workflow_engineering.structured_output import call_structured_tool


class EvaluationStatus(StrEnum):
    """Possible outcomes of recommendation evaluation."""

    PASS = "pass"
    NEEDS_REVISION = "needs_revision"


class SemanticEvaluationOutput(BaseModel):
    """Structured semantic evaluation returned by Claude."""

    status: EvaluationStatus

    feedback: list[str] = Field(
        default_factory=list,
        description=(
            "Actionable feedback when revision is required. "
            "May be empty when the recommendation passes."
        ),
    )

    @model_validator(mode="after")
    def validate_feedback(self) -> "SemanticEvaluationOutput":
        """Require actionable feedback when revision is requested."""
        if (
            self.status == EvaluationStatus.NEEDS_REVISION
            and not self.feedback
        ):
            raise ValueError(
                "Evaluator feedback is required when "
                "status is needs_revision."
            )

        return self


class RentalRecommendationEvaluator:
    """Evaluate rental recommendations using semantic judgment."""

    def __init__(self, client: Anthropic) -> None:
        """Initialize the evaluator with an Anthropic client."""
        self._client = client

    def evaluate(
        self,
        user_request: str,
        intent: RentalSearchIntent,
        candidates: list[RentalProperty],
        recommendation: RentalRecommendationOutput,
    ) -> SemanticEvaluationOutput:
        """Evaluate recommendation quality and preference alignment."""
        return call_structured_tool(
            client=self._client,
            system_prompt=load_prompt(
                "rental_recommendation_evaluator.txt"
            ),
            user_message=self._build_evaluation_message(
                user_request,
                intent,
                candidates,
                recommendation,
            ),
            tool_name="record_rental_evaluation",
            tool_description=(
                "Record whether the rental recommendation passes "
                "semantic evaluation. When revision is required, "
                "include specific actionable feedback."
            ),
            output_model=SemanticEvaluationOutput,
            max_tokens=1200,
        )

    @staticmethod
    def _build_evaluation_message(
        user_request: str,
        intent: RentalSearchIntent,
        candidates: list[RentalProperty],
        recommendation: RentalRecommendationOutput,
    ) -> str:
        """Build the evidence package used for semantic evaluation."""
        payload: dict[str, Any] = {
            "original_request": user_request,
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
            "interpreted_preferences": [
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
            "recommendation": {
                "recommended_property_id": (
                    recommendation.recommended_property_id
                ),
                "reasoning": recommendation.reasoning,
                "tradeoffs": recommendation.tradeoffs,
            },
        }

        return json.dumps(payload, indent=2)
