"""Orchestrator-worker workflow for legal case preparation.

Author: Gaurav Thakur

Description:
Coordinates dynamic legal case task planning, concurrent worker execution,
failure isolation, and final synthesis. Claude determines which substantial
analysis tasks are required, while the application owns execution,
concurrency, failure handling, stopping, and result collection.

This workflow is for educational purposes only and does not provide legal
advice.
"""

import asyncio

from anthropic import Anthropic
from pydantic import BaseModel

from workflow_engineering.orchestrators.legal_case_orchestrator import (
    ExecutionPlan,
    create_execution_plan,
)
from workflow_engineering.synthesizers.legal_case_synthesizer import (
    CasePreparationSummary,
    synthesize_case_preparation,
)
from workflow_engineering.workers.legal_case_worker import analyze_case_task
from workflow_engineering.workflows.legal_case_execution import (
    FailedWorkerExecution,
    SuccessfulWorkerExecution,
    WorkerExecution,
)


class LegalCaseWorkflowResult(BaseModel):
    """Complete result of the legal case preparation workflow."""

    execution_plan: ExecutionPlan
    worker_executions: list[WorkerExecution]
    case_preparation_summary: CasePreparationSummary


async def run_legal_case_workflow(
    *,
    client: Anthropic,
    case_description: str,
) -> LegalCaseWorkflowResult:
    """Plan, execute, and synthesize legal case preparation work.

    The orchestrator dynamically determines which analysis tasks are required.
    Each independent task is executed concurrently by the generic case-analysis
    worker. Worker failures are isolated so successful results remain
    available. The synthesizer then consolidates the completed worker results
    and explicitly identifies analysis areas that remain incomplete.
    """
    normalized_case = case_description.strip()

    if not normalized_case:
        raise ValueError("Case description must not be empty.")

    execution_plan = create_execution_plan(
        client=client,
        case_description=normalized_case,
    )

    worker_tasks = [
        asyncio.to_thread(
            analyze_case_task,
            client=client,
            case_description=normalized_case,
            task=task,
        )
        for task in execution_plan.tasks
    ]

    worker_outputs = await asyncio.gather(
        *worker_tasks,
        return_exceptions=True,
    )

    worker_executions: list[WorkerExecution] = []

    for task, output in zip(
        execution_plan.tasks,
        worker_outputs,
        strict=True,
    ):
        if isinstance(output, BaseException):
            worker_executions.append(
                FailedWorkerExecution(
                    task=task,
                    error_type=type(output).__name__,
                    error_message=str(output),
                )
            )
            continue

        if output.task_id != task.task_id:
            worker_executions.append(
                FailedWorkerExecution(
                    task=task,
                    error_type="TaskIdentityMismatch",
                    error_message=(
                        "Worker returned task_id "
                        f"{output.task_id!r} for assigned task "
                        f"{task.task_id!r}."
                    ),
                )
            )
            continue

        worker_executions.append(
            SuccessfulWorkerExecution(
                task=task,
                result=output,
            )
        )

    case_preparation_summary = synthesize_case_preparation(
        client=client,
        case_description=normalized_case,
        execution_plan=execution_plan,
        worker_executions=worker_executions,
    )

    return LegalCaseWorkflowResult(
        execution_plan=execution_plan,
        worker_executions=worker_executions,
        case_preparation_summary=case_preparation_summary,
    )