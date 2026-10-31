"""Claude orchestrator for legal case preparation.

Author: Gaurav Thakur

Description:
Decomposes a client-provided legal case description into a bounded,
structured execution plan for downstream case-analysis workers.
"""

from anthropic import Anthropic
from pydantic import BaseModel, Field

from workflow_engineering.prompt_loader import load_prompt
from workflow_engineering.structured_output import call_structured_tool

_MAX_ORCHESTRATION_TASKS = 6
_MAX_TOKENS = 1200
_ORCHESTRATOR_PROMPT_FILE = "legal_case_orchestrator.txt"


class CaseTask(BaseModel):
    """A substantial unit of case-analysis work created by the orchestrator."""

    task_id: str = Field(
        min_length=1,
        description="Unique identifier for this task within the execution plan.",
    )
    title: str = Field(
        min_length=1,
        description="Short descriptive title for the analysis task.",
    )
    objective: str = Field(
        min_length=1,
        description="Clear description of what the worker must analyze.",
    )


class ExecutionPlan(BaseModel):
    """Structured plan containing the work required for a client case."""

    tasks: list[CaseTask] = Field(
        min_length=1,
        max_length=_MAX_ORCHESTRATION_TASKS,
        description=(
            "Distinct analysis tasks required to prepare the provided case."
        ),
    )


def create_execution_plan(
    *,
    client: Anthropic,
    case_description: str,
) -> ExecutionPlan:
    """Create a validated execution plan for a client case.

    Args:
        client: Configured Anthropic client.
        case_description: Natural-language description of the client's case.

    Returns:
        A validated execution plan containing dynamically generated tasks.

    Raises:
        ValueError: If the case description is empty.
        RuntimeError: If Claude cannot produce a valid execution plan.
    """
    normalized_case = case_description.strip()

    if not normalized_case:
        raise ValueError("Case description must not be empty.")

    return call_structured_tool(
        client=client,
        system_prompt=load_prompt(_ORCHESTRATOR_PROMPT_FILE),
        user_message=(
            "Create an execution plan for the following client case.\n\n"
            f"CASE DESCRIPTION:\n{normalized_case}"
        ),
        tool_name="create_execution_plan",
        tool_description=(
            "Return the structured analysis plan for the provided client case."
        ),
        output_model=ExecutionPlan,
        max_tokens=_MAX_TOKENS,
    )