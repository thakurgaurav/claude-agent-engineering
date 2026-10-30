"""Orchestrate the rental Evaluator-Optimizer workflow.

Author: Gaurav Thakur

Description:
Orchestrates rental intent interpretation, selection, evaluation, and revision.
"""

from dataclasses import dataclass

from workflow_engineering.domain.rental import RentalProperty
from workflow_engineering.evaluators.rental_recommendation_evaluator import (
    EvaluationStatus,
    RentalRecommendationEvaluator,
    SemanticEvaluationOutput,
)
from workflow_engineering.generators.rental_recommendation_generator import (
    RentalRecommendationGenerator,
    RentalRecommendationOutput,
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


@dataclass(frozen=True)
class RentalSelectionResult:
    """Final result produced by the rental selection workflow."""

    recommendation: RentalRecommendationOutput
    evaluation: SemanticEvaluationOutput
    optimization_iterations: int


class RentalSelectionWorkflow:
    """Run the rental selection Evaluator-Optimizer workflow."""

    def __init__(
        self,
        interpreter: RentalRequirementInterpreter,
        repository: RentalPropertyRepository,
        generator: RentalRecommendationGenerator,
        evaluator: RentalRecommendationEvaluator,
        optimizer: RentalRecommendationOptimizer,
        *,
        candidate_limit: int = 10,
        max_optimization_iterations: int = 2,
    ) -> None:
        """Initialize the workflow with its required components."""
        if candidate_limit <= 0:
            raise ValueError("Candidate limit must be greater than zero.")

        if max_optimization_iterations < 0:
            raise ValueError(
                "Maximum optimization iterations cannot be negative."
            )

        self._interpreter = interpreter
        self._repository = repository
        self._generator = generator
        self._evaluator = evaluator
        self._optimizer = optimizer
        self._candidate_limit = candidate_limit
        self._max_optimization_iterations = (
            max_optimization_iterations
        )

    def run(self, user_request: str) -> RentalSelectionResult:
        """Run rental selection until it passes or reaches the iteration limit."""
        intent = self._interpreter.interpret(user_request)

        candidates = self._repository.find_candidates(
            intent.criteria,
            limit=self._candidate_limit,
        )

        self._require_candidates(candidates)

        recommendation = self._generator.generate(
            user_request,
            intent,
            candidates,
        )

        evaluation = self._evaluator.evaluate(
            user_request,
            intent,
            candidates,
            recommendation,
        )

        optimization_iterations = 0

        while (
            evaluation.status == EvaluationStatus.NEEDS_REVISION
            and optimization_iterations
            < self._max_optimization_iterations
        ):
            recommendation = self._optimizer.optimize(
                user_request,
                intent,
                candidates,
                recommendation,
                evaluation.feedback,
            )

            optimization_iterations += 1

            evaluation = self._evaluator.evaluate(
                user_request,
                intent,
                candidates,
                recommendation,
            )

        return RentalSelectionResult(
            recommendation=recommendation,
            evaluation=evaluation,
            optimization_iterations=optimization_iterations,
        )

    @staticmethod
    def _require_candidates(
        candidates: list[RentalProperty],
    ) -> None:
        """Fail clearly when hard constraints produce no candidates."""
        if not candidates:
            raise ValueError(
                "No rental properties satisfy the hard constraints."
            )
