"""Claude worker for focused legal case analysis.

Author: Gaurav Thakur

Description:
Executes one orchestrator-generated legal case analysis task and returns
validated findings for downstream workflow synthesis.
"""

from anthropic import Anthropic
from pydantic import BaseModel, Field

from workflow_engineering.orchestrators.legal_case_orchestrator import CaseTask
from workflow_engineering.prompt_loader import load_prompt
from workflow_engineering.structured_output import call_structured_tool

_MAX_TOKENS = 3000
_WORKER_PROMPT_FILE = "legal_case_worker.txt"


class WorkerResult(BaseModel):
    """Validated result produced by one case-analysis worker."""

    task_id: str = Field(
        min_length=1,
        description="Identifier of the orchestrator task being analyzed.",
    )
    findings: list[str] = Field(
        min_length=1,
        description="Substantive findings produced for the assigned task.",
    )
    uncertainties: list[str] = Field(
        default_factory=list,
        description=(
            "Missing facts, ambiguities, or limitations affecting the analysis."
        ),
    )
    verification_items: list[str] = Field(
        default_factory=list,
        description=(
            "Legal rules, deadlines, jurisdiction-specific matters, or other "
            "points that require verification against authoritative sources."
        ),
    )


def analyze_case_task(
    *,
    client: Anthropic,
    case_description: str,
    task: CaseTask,
) -> WorkerResult:
    """Execute one orchestrator-generated case-analysis task.

    Args:
        client: Configured Anthropic client.
        case_description: Original natural-language client case description.
        task: Specific analysis task assigned by the orchestrator.

    Returns:
        Validated analysis produced for the assigned task.

    Raises:
        ValueError: If the case description is empty.
        RuntimeError: If Claude cannot produce valid structured output.
    """
    normalized_case = case_description.strip()

    if not normalized_case:
        raise ValueError("Case description must not be empty.")

    return call_structured_tool(
        client=client,
        system_prompt=load_prompt(_WORKER_PROMPT_FILE),
        user_message=(
            "Analyze the assigned task using only the provided case facts "
            "and your general reasoning.\n\n"
            f"CASE DESCRIPTION:\n{normalized_case}\n\n"
            f"TASK ID:\n{task.task_id}\n\n"
            f"TASK TITLE:\n{task.title}\n\n"
            f"TASK OBJECTIVE:\n{task.objective}"
        ),
        tool_name="submit_worker_result",
        tool_description=(
            "Return the structured analysis result for the assigned case task."
        ),
        output_model=WorkerResult,
        max_tokens=_MAX_TOKENS,
    )