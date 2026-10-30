"""Demonstrate Claude-based rental recommendation generation.

Author: Gaurav Thakur

Description:
Demonstrates generating a rental recommendation from MongoDB candidates.
"""

from claude_engineering.claude_client import create_claude_client
from pymongo import MongoClient

from workflow_engineering.config import get_mongodb_settings
from workflow_engineering.generators.rental_recommendation_generator import (
    RentalRecommendationGenerator,
)
from workflow_engineering.interpreters.rental_requirement_interpreter import (
    RentalRequirementInterpreter,
)
from workflow_engineering.repositories.rental_property_repository import (
    RentalPropertyRepository,
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


def main() -> None:
    """Run the rental recommendation generator demo."""
    claude_client = create_claude_client()
    interpreter = RentalRequirementInterpreter(claude_client)
    generator = RentalRecommendationGenerator(claude_client)

    intent = interpreter.interpret(USER_REQUEST)

    mongodb_config = get_mongodb_settings()

    with MongoClient(mongodb_config.uri) as mongo_client:
        collection = mongo_client[
            mongodb_config.database
        ][mongodb_config.properties_collection]

        repository = RentalPropertyRepository(collection)

        candidates = repository.find_candidates(
            intent.criteria,
            limit=10,
        )

        recommendation = generator.generate(
            USER_REQUEST,
            intent,
            candidates,
        )

    print("\nInitial Recommendation")
    print("======================")
    print(
        "Property:",
        recommendation.recommended_property_id,
    )
    print("\nReasoning:")
    print(recommendation.reasoning)

    print("\nTradeoffs:")
    for tradeoff in recommendation.tradeoffs:
        print(f"- {tradeoff}")


if __name__ == "__main__":
    main()
