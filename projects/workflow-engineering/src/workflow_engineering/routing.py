"""Decision routing and route-specific research plan generation.

Author:
    Gaurav Thakur
Description:
    Classifies decisions and creates specialized research plans for each
    supported decision route.
"""

from enum import StrEnum

from workflow_engineering.model import call_model
from workflow_engineering.prompt_chain import (
    define_evaluation_criteria,
    extract_constraints,
    understand_decision,
)
from workflow_engineering.prompt_loader import load_prompt


class DecisionRoute(StrEnum):
    """Supported routing destinations for decision requests.

    Author:
        Gaurav Thakur
    Description:
        Enumerates the route categories used by the decision router.
    """

    PURCHASE = "PURCHASE"
    CAREER = "CAREER"
    TRAVEL = "TRAVEL"
    GENERAL = "GENERAL"


def run_routing_workflow(decision_request: str) -> tuple[DecisionRoute, str]:
    """Run a decision request through the routing workflow.
    
    Args:
        decision_request: Natural-language description of the user's decision.
    
    Returns:
        The selected route and the route-specific decision plan.
    """
    decision_understanding = understand_decision(decision_request)

    constraints = extract_constraints(decision_understanding)

    evaluation_criteria = define_evaluation_criteria(constraints)

    route = route_decision(decision_understanding)

    plan = create_plan_for_route(
        route,
        decision_understanding,
        constraints,
        evaluation_criteria,
    )

    return route, plan


def route_decision(decision_understanding: str) -> DecisionRoute:
    """Classify a decision into one of the application's supported routes.

    Args:
        decision_understanding: Normalized description of the user's decision.

    Returns:
        The validated route selected for the decision.

    Raises:
        ValueError: If Claude returns an unsupported route.
    """
    prompt_template = load_prompt("route_decision.txt")
    prompt = prompt_template.format(
        decision_understanding=decision_understanding
    )

    model_output = call_model(
        prompt,
        max_tokens=20,
        thinking_enabled=False,
    )

    return DecisionRoute(model_output.strip())


def create_plan_for_route(
    route: DecisionRoute,
    decision_understanding: str,
    constraints: str,
    evaluation_criteria: str,
) -> str:
    """Execute the planning path associated with the selected route.
     
    Args:
        route: The selected route for the decision.
        decision_understanding: Normalized description of the user's decision.
        constraints: Hard constraints, preferences and relevant unknowns.
        evaluation_criteria: Criteria used to compare candidate options.
        
    Returns:
        A route-specific research plan for the decision.
    """
    match route:
        case DecisionRoute.PURCHASE:
            return create_purchase_plan(
                decision_understanding,
                constraints,
                evaluation_criteria,
            )
        
        case DecisionRoute.CAREER:
            return create_career_plan(
                decision_understanding,
                constraints,
                evaluation_criteria,
            )
        
        case DecisionRoute.TRAVEL:
            return create_travel_plan(
                decision_understanding,
                constraints,
                evaluation_criteria,
            )
        
        case DecisionRoute.GENERAL:
            return create_general_plan(
                decision_understanding,
                constraints,
                evaluation_criteria,
            )

        case _:
            raise ValueError(f"Unsupported route: {route}")
    


def _create_plan(
    prompt_name: str,
    decision_understanding: str,
    constraints: str,
    evaluation_criteria: str,
) -> str:
    """Create a plan using the shared planning prompt and model settings."""
    prompt_template = load_prompt(prompt_name)
    prompt = prompt_template.format(
        decision_understanding=decision_understanding,
        constraints=constraints,
        evaluation_criteria=evaluation_criteria,
    )

    return call_model(
        prompt,
        max_tokens=2000,
        thinking_enabled=False,
    )


def create_purchase_plan(
    decision_understanding: str,
    constraints: str,
    evaluation_criteria: str,
) -> str:
    """Create a research plan specialized for purchase decisions.

    Args:
        decision_understanding: Normalized description of the user's decision.
        constraints: Hard constraints, preferences and relevant unknowns.
        evaluation_criteria: Criteria used to compare candidate options.

    Returns:
        A purchase-focused research plan.
    """
    return _create_plan(
        "create_purchase_plan.txt",
        decision_understanding,
        constraints,
        evaluation_criteria,
    )


def create_career_plan(
    decision_understanding: str,
    constraints: str,
    evaluation_criteria: str,
) -> str:
    """Create a research plan specialized for career decisions.

    Args:
        decision_understanding: Normalized description of the user's decision.
        constraints: Hard constraints, preferences and relevant unknowns.
        evaluation_criteria: Criteria used to compare candidate options.
    Returns:
        A career-focused research plan.
    """
    return _create_plan(
        "create_career_plan.txt",
        decision_understanding,
        constraints,
        evaluation_criteria,
    )


def create_travel_plan(
    decision_understanding: str,
    constraints: str,
    evaluation_criteria: str,
) -> str:
    """Create a research plan specialized for travel decisions.

    Args:
        decision_understanding: Normalized description of the user's decision.
        constraints: Hard constraints, preferences and relevant unknowns.
        evaluation_criteria: Criteria used to compare candidate options.
    Returns:
        A travel-focused research plan.
    """
    return _create_plan(
        "create_travel_plan.txt",
        decision_understanding,
        constraints,
        evaluation_criteria,
    )


def create_general_plan(
    decision_understanding: str,
    constraints: str,
    evaluation_criteria: str,
) -> str:
    """Create a research plan specialized for general decisions.

    Args:
        decision_understanding: Normalized description of the user's decision.
        constraints: Hard constraints, preferences and relevant unknowns.
        evaluation_criteria: Criteria used to compare candidate options.
    Returns:
        A general-purpose research plan.
    """
    return _create_plan(
        "create_general_plan.txt",
        decision_understanding,
        constraints,
        evaluation_criteria,
    )
