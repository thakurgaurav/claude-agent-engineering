"""Interpret natural-language rental requirements into structured intent.

Author: Gaurav Thakur

Description:
Converts natural-language rental requests into structured search intent.
"""

from typing import Literal

from anthropic import Anthropic
from claude_engineering.constants import CLAUDE_MODEL
from pydantic import BaseModel, Field

from workflow_engineering.domain.rental import (
    PreferencePriority,
    RentalPreference,
    RentalPreferenceAttribute,
    RentalSearchCriteria,
    RentalSearchIntent,
)
from workflow_engineering.prompt_loader import load_prompt


class RentalPreferenceOutput(BaseModel):
    """Semantic rental preference extracted from a user's request."""

    attribute: Literal[
        "safety",
        "space",
        "newness",
        "walkability",
        "schools",
        "transit",
        "in_unit_laundry",
        "gym",
        "pool",
        "air_conditioning",
        "furnished",
    ]
    priority: Literal["low", "medium", "high", "very_high"]
    description: str


class RentalIntentOutput(BaseModel):
    """Structured output expected from Claude's requirement interpretation."""

    city: str
    max_monthly_rent: int | None = None
    min_bedrooms: int | None = None
    min_bathrooms: int | None = None
    pets_required: bool = False
    parking_required: bool = False
    property_type: str | None = None

    preferences: list[RentalPreferenceOutput] = Field(default_factory=list)
    unsupported_requirements: list[str] = Field(default_factory=list)
    

class RentalRequirementInterpreter:
    """Interpet natural language rental requirements using claude."""
    
    def __init__(self, client:Anthropic) -> None:
        """Initialize the interpreter with the shared Claude client."""
        self._client = client
        
    def interpret(self, user_request: str) -> RentalSearchIntent:
        """Interpret a natural language request into structure intent."""
        if not user_request.strip():
            raise ValueError("Rental request must not be empty.")
        
        system_prompt = load_prompt("rental_requirement_interpreter.txt")
        
        response = self._client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            system=system_prompt,
            tools=[
                {
                    "type": "custom",
                    "name": "record_rental_intent",
                    "description": (
                        "Record the structured interpretation of the renter's "
                        "requirements."
                        ),
                    "input_schema": RentalIntentOutput.model_json_schema(),
                    }
                ],
            tool_choice= {
                "type": "tool",
                "name": "record_rental_intent",
            },
            messages=[
                {
                    "role": "user",
                    "content": user_request,
                },
            ],
        )
        
        tool_blocks = [
            block
            for block in response.content
            if block.type == "tool_use"
            and block.name == "record_rental_intent"
        ]
        
        if len(tool_blocks) != 1:
            raise RuntimeError (
                "Claude did not return exactly one rental intent. "
                f"stop_reason={response.stop_reason}"
            )
            
        output = RentalIntentOutput.model_validate(tool_blocks[0].input)
        
        criteria = RentalSearchCriteria(
            city = output.city,
            max_monthly_rent=output.max_monthly_rent,
            min_bedrooms=output.min_bedrooms,
            min_bathrooms=output.min_bathrooms,
            pets_required=output.pets_required,
            parking_required=output.parking_required,
            property_type=output.property_type,
        )
        
        preferences = tuple(
            RentalPreference(
                attribute=RentalPreferenceAttribute(preference.attribute),
                priority=PreferencePriority(preference.priority),
                description=preference.description,
                )
            for preference in output.preferences
            )
        
        
        return RentalSearchIntent(
            criteria=criteria,
            preferences=preferences,
            unsupported_requirements=tuple(
                output.unsupported_requirements
                ),
            )
