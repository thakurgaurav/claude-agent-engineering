from urllib import response

from claude_engineering.config import get_anthropic_api_key
from workflow_engineering.prompt_loader import load_prompt
from claude_engineering.constants import CLAUDE_MODEL
from anthropic import Anthropic


_client: Anthropic | None = None


def get_claude_client() -> Anthropic:
    """Return the process-level Claude API client, creating it when first needed."""
    global _client

    if _client is None:
        _client = Anthropic(api_key=get_anthropic_api_key())

    return _client

def _call_model(
    prompt: str,
    *,
    max_tokens: int = 600,
    thinking_enabled: bool = False,
) -> str:
    """Send a prompt to Claude using configurable inference settings."""
    client = get_claude_client()

    kwargs = {
        "model": CLAUDE_MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }

    if not thinking_enabled:
        kwargs["thinking"] = {"type": "disabled"}

    response = client.messages.create(**kwargs)


    text_blocks = [
        block.text
        for block in response.content
        if block.type == "text"
    ]

    if not text_blocks:
      raise RuntimeError(
        f"Claude response contained no text. "
        f"stop_reason={response.stop_reason}"
    )

    if response.stop_reason == "max_tokens":
      raise RuntimeError(
        f"Claude response was truncated after "
        f"{response.usage.output_tokens} output tokens."
    )


    return "\n".join(text_blocks)


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

    return _call_model(
        prompt,
        max_tokens=1000,
    )
    """Identify and normalize the decision the user is trying to make.

    Args:
        decision_request: Natural-language description of the user's decision.

    Returns:
        A concise description of the decision, goal, and available options.
    """

    prompt=f"""Analyze the following decision request.

Identify:
- The decision user needs to make
- The user's primary goal
- any options already mentioned
- important context explicitly provided

Do not recommend an option.
Do not invent missing information.

Decision request:
{decision_request}
"""
    return _call_model(prompt, max_tokens= 400)


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

    return _call_model(
        prompt,
        max_tokens=1000,
    )
    """Extract constraints and preferences from the understood decision.

    Args:
        decision_understanding: Normalized decision information produced by previous workflow stage.

    Returns:
        Hard constraints, soft preferences, and important unknowns.
    """

    prompt= f"""Analyze the following decision description.

Separate the information into:

1. Hard constraints
   Requirements that must be satisfied.

2. Soft preferences
   Requirements that are important buy may be negotiable.

3. Unknowns
   Missing information that could materially affect the decision.

Do not recomment any option.
Do not invent missing information.
{decision_understanding}
"""
    return _call_model(prompt, max_tokens=800)


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

    return _call_model(
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

    return _call_model(
        prompt,
        max_tokens=2000,
    )


if __name__ == "__main__":
    #request = """
    #I need a laptop under $1,500 for Java development,
    #AI experimentation, and occasional video editing.
    #Battery life is important and I want to keep it for
    #at least five years.
    #"""

    request = """
    I need to plan 7 days trip to Hawaii with my family. 
    We want to visit the beaches, go hiking, water sports, enjoy in the nature.
    As family includes 2 adults and 3 kids, we need to find a family-friendly accommodation.
    With little kids, we dont want a hectic schedule, it should be relaxing. 
    Looking for some good package deals which includes accommodation, sightseeing and activities.
"""

    result = run_prompt_chain(request)
    print(result)
