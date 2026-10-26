"""Prompt-chaining workflow for structured decision analysis.

Author:
    Gaurav Thakur
Description:
    Runs the decision-understanding, constraint-extraction, evaluation, and
    research-planning stages of the workflow.
"""

from enum import StrEnum

from workflow_engineering.model import call_model
from workflow_engineering.prompt_loader import load_prompt


class DecisionRoute(StrEnum):
    """Supported routing destinations for decision requests.

    Author:
        Gaurav Thakur
    Description:
        Enumerates the route categories returned by the decision router.
    """

    PURCHASE = "PURCHASE"
    CAREER = "CAREER"
    TRAVEL = "TRAVEL"
    GENERAL = "GENERAL"



def run_prompt_chain(decision_request: str) -> str:
    """Run the decision-analysis prompt chain.

    Args:
        decision_request: Natural-language description of the user's decision.

    Returns:
        The result produced by the decision workflow.
    """

    decision_understanding = understand_decision(decision_request)
    
    constraints = extract_constraints(decision_understanding)

    evaluation_criteria = define_evaluation_criteria(constraints)

    research_plan = create_research_plan(decision_understanding, evaluation_criteria)

    return research_plan


def understand_decision(decision_request: str) -> str:
    """Identify and normalize the decision the user is trying to make.

    Args:
        decision_request: Natural-language description of the user's decision.

    Returns:
        A concise description of the decision, goal, and available options.
    """
    prompt_template = load_prompt("understand_decision.txt")
    prompt = prompt_template.format(decision_request=decision_request)

    return call_model(
        prompt,
        max_tokens=1000,)
        
    

def extract_constraints(decision_understanding: str) -> str:
    """Extract constraints and preferences from the understood decision.

    Args:
        decision_understanding: Normalized decision information produced by
            the previous workflow stage.

    Returns:
        Hard constraints, soft preferences, and important unknowns.
    """
    prompt_template = load_prompt("extract_constraints.txt")
    prompt = prompt_template.format(
        decision_understanding=decision_understanding
    )

    return call_model(
        prompt,
        max_tokens=1000,)



def define_evaluation_criteria(constraints: str) -> str:
    """Define criteria for evaluating candidate decision options.

    Args:
        constraints: Hard constraints, soft preferences, and unknowns
            identified by the previous workflow stage.

    Returns:
        Evaluation criteria and the evidence needed to assess them.
    """
    prompt_template = load_prompt("define_evaluation_criteria.txt")
    prompt = prompt_template.format(constraints=constraints)

    return call_model(
        prompt,
        max_tokens=1000,
    )


def create_research_plan(
    decision_understanding: str,
    evaluation_criteria: str,
) -> str:
    """Create an evidence-oriented research plan for the decision.

    Args:
        decision_understanding: Normalized description of the user's decision.
        evaluation_criteria: Criteria that candidate options will be evaluated against.

    Returns:
        A prioritized plan describing what evidence should be researched.
    """
    prompt_template = load_prompt("create_research_plan.txt")
    prompt = prompt_template.format(
        decision_understanding=decision_understanding,
        evaluation_criteria=evaluation_criteria,
    )

    return call_model(
        prompt,
        max_tokens=2000,
    )



def route_decision(decision_understanding: str) -> DecisionRoute:
    """ Classify the decision into one of the supported routes.
    
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

