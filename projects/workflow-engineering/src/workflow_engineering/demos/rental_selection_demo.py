"""Run the complete rental Evaluator-Optimizer workflow.

Author: Gaurav Thakur

Description:
Demonstrates the complete rental evaluator-optimizer workflow.
"""

from claude_engineering.claude_client import create_claude_client
from pymongo import MongoClient

# Use the same settings import already working in rental_repository_demo.py.
from workflow_engineering.config import get_mongodb_settings
from workflow_engineering.evaluators.rental_recommendation_evaluator import (
    RentalRecommendationEvaluator,
)
from workflow_engineering.generators.rental_recommendation_generator import (
    RentalRecommendationGenerator,
)
from workflow_engineering.interpreters.rental_requirement_interpreter import (
    RentalRequirementInterpreter,
)
from workflow_engineering.optimizers.rental_recommendation_optimizer import (
    RentalRecommendationOptimizer,
)
from workflow_engineering.repositories.rental_property_repository import (
    RentalPropertyRepository,
)
from workflow_engineering.workflows.rental_selection_workflow import (
    RentalSelectionWorkflow,
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

USER_REQUEST1 = """
I'm looking for a 2-bedroom apartment in San Jose under $3,500. Pets must be allowed and parking is required.
Safety is very important, but I do not want you to automatically choose the property with the highest safety score. I care equally about having a spacious apartment and a reasonably newer property. A small improvement in safety is not worth giving up a lot of space or choosing a much older apartment.
In-unit laundry is important. I would prefer air conditioning, but it is not essential. A gym and pool should have very little influence on the decision.
Choose the property with the best overall balance. When two properties are close, explicitly compare what I gain and lose with each before deciding.
"""


def main() -> None:
    """Run and display the complete rental selection workflow."""
    claude_client = create_claude_client()
    mongodb_settings = get_mongodb_settings()

    interpreter = RentalRequirementInterpreter(claude_client)
    generator = RentalRecommendationGenerator(claude_client)
    evaluator = RentalRecommendationEvaluator(claude_client)
    optimizer = RentalRecommendationOptimizer(claude_client)

    with MongoClient(mongodb_settings.uri) as mongo_client:
        collection = mongo_client[
            mongodb_settings.database
        ][mongodb_settings.properties_collection]

        repository = RentalPropertyRepository(collection)

        workflow = RentalSelectionWorkflow(
            interpreter=interpreter,
            repository=repository,
            generator=generator,
            evaluator=evaluator,
            optimizer=optimizer,
            candidate_limit=10,
            max_optimization_iterations=2,
        )

        result = workflow.run(USER_REQUEST)

    print("\nFinal Recommendation")
    print("====================")
    print(
        "Property:",
        result.recommendation.recommended_property_id,
    )

    print("\nReasoning:")
    print(result.recommendation.reasoning)

    print("\nTradeoffs:")
    if result.recommendation.tradeoffs:
        for tradeoff in result.recommendation.tradeoffs:
            print(f"- {tradeoff}")
    else:
        print("- None")

    print("\nFinal Evaluation")
    print("================")
    print("Status:", result.evaluation.status.value)
    print(
        "Optimization iterations:",
        result.optimization_iterations,
    )

    if result.evaluation.feedback:
        print("\nFeedback:")
        for feedback in result.evaluation.feedback:
            print(f"- {feedback}")
    else:
        print("Feedback: None")


if __name__ == "__main__":
    main()
