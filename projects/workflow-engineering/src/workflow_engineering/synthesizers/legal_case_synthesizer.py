"""Claude synthesizer for legal case preparation.

Author: Gaurav Thakur

Description:
Consolidates distributed legal case worker results into a coherent,
validated case-preparation summary. The synthesizer operates only on the
case context and workflow outputs supplied to it; it does not replace failed
worker analysis or provide independent legal advice.
"""

import json

from anthropic import Anthropic
from pydantic import BaseModel, Field
from workflow_engineering.orchestrators.legal_case_orchestrator import (
    ExecutionPlan,
)
from workflow_engineering.prompt_loader import load_prompt
from workflow_engineering.structured_output import call_structured_tool
from workflow_engineering.workflows.legal_case_execution import (
    FailedWorkerExecution,
    SuccessfulWorkerExecution,
    WorkerExecution,
)

_MAX_TOKENS = 3000
_SYNTHESIZER_PROMPT_FILE = "legal_case_synthesizer.txt"


class CasePreparationSummary(BaseModel):
    """Consolidated summary of the distributed case-preparation analysis."""

    overview: str = Field(
        min_length=1,
        description=(
            "Concise overall picture produced from the completed worker analysis."
        ),
    )
    key_findings: list[str] = Field(
        default_factory=list,
        description=(
            "Most important findings consolidated across successful workers."
        ),
    )
    uncertainties: list[str] = Field(
        default_factory=list,
        description=(
            "Material missing, ambiguous, or conflicting facts consolidated "
            "across successful workers."
        ),
    )
    verification_items: list[str] = Field(
        default_factory=list,
        description=(
            "Consolidated legal or procedural matters requiring verification "
            "against authoritative and current sources."
        ),
    )
    incomplete_areas: list[str] = Field(
        default_factory=list,
        description=(
            "Areas of analysis that remain incomplete because worker execution "
            "failed or did not produce a usable result."
        ),
    )


def synthesize_case_preparation(
    *,
    client: Anthropic,
    case_description: str,
    execution_plan: ExecutionPlan,
    worker_executions: list[WorkerExecution],
) -> CasePreparationSummary:
    """Synthesize completed worker analysis into one case-preparation summary."""
    normalized_case = case_description.strip()

    if not normalized_case:
        raise ValueError("Case description must not be empty.")

    synthesis_context = _build_synthesis_context(
        execution_plan=execution_plan,
        worker_executions=worker_executions,
    )

    return call_structured_tool(
        client=client,
        system_prompt=load_prompt(_SYNTHESIZER_PROMPT_FILE),
        user_message=(
            "Synthesize the completed case-preparation workflow into one "
            "coherent summary.\n\n"
            f"CASE DESCRIPTION:\n{normalized_case}\n\n"
            "WORKFLOW OUTPUTS:\n"
            f"{json.dumps(synthesis_context, indent=2)}"
        ),
        tool_name="submit_case_preparation_summary",
        tool_description=(
            "Return the consolidated case-preparation summary derived from "
            "the workflow outputs."
        ),
        output_model=CasePreparationSummary,
        max_tokens=_MAX_TOKENS,
    )


def _build_synthesis_context(
    *,
    execution_plan: ExecutionPlan,
    worker_executions: list[WorkerExecution],
) -> dict[str, object]:
    """Build a serializable synthesis context from workflow execution results."""
    planned_tasks = [
        task.model_dump()
        for task in execution_plan.tasks
    ]

    successful_results: list[dict[str, object]] = []
    failed_results: list[dict[str, object]] = []

    for execution in worker_executions:
        if isinstance(execution, SuccessfulWorkerExecution):
            successful_results.append(
                {
                    "task": execution.task.model_dump(),
                    "result": execution.result.model_dump(),
                }
            )
            continue

        if isinstance(execution, FailedWorkerExecution):
            failed_results.append(
                {
                    "task": execution.task.model_dump(),
                    "error_type": execution.error_type,
                    "error_message": execution.error_message,
                }
            )
            continue

        raise TypeError(
            "Unsupported worker execution type: "
            f"{type(execution).__name__}"
        )

    return {
        "execution_plan": planned_tasks,
        "successful_worker_results": successful_results,
        "failed_worker_results": failed_results,
    }