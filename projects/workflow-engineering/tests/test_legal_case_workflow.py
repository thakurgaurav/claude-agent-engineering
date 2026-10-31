"""Tests for the legal case orchestrator-worker workflow.

Author: Gaurav Thakur

Description:
Verifies workflow coordination, worker failure isolation, successful-result
preservation, and synthesis invocation without making real Claude API calls.
"""

from unittest.mock import Mock

import pytest
from workflow_engineering.orchestrators.legal_case_orchestrator import (
    CaseTask,
    ExecutionPlan,
)
from workflow_engineering.synthesizers.legal_case_synthesizer import (
    CasePreparationSummary,
)
from workflow_engineering.workers.legal_case_worker import WorkerResult
from workflow_engineering.workflows.legal_case_execution import (
    FailedWorkerExecution,
    SuccessfulWorkerExecution,
)
from workflow_engineering.workflows.legal_case_workflow import (
    run_legal_case_workflow,
)


@pytest.mark.asyncio
async def test_workflow_isolates_worker_failure_and_continues_to_synthesis(
    monkeypatch,
) -> None:
    """Ensure one worker failure does not discard successful worker results."""
    task_1 = CaseTask(
        task_id="T1",
        title="Chronology Analysis",
        objective="Analyze the sequence of relevant events.",
    )
    task_2 = CaseTask(
        task_id="T2",
        title="Evidence Review",
        objective="Analyze the available documentary evidence.",
    )
    task_3 = CaseTask(
        task_id="T3",
        title="Comparator Analysis",
        objective="Analyze relevant comparator information.",
    )

    execution_plan = ExecutionPlan(
        tasks=[task_1, task_2, task_3],
    )

    worker_result_1 = WorkerResult(
        task_id="T1",
        findings=["Chronology analysis completed."],
        uncertainties=[],
        verification_items=[],
    )
    worker_result_3 = WorkerResult(
        task_id="T3",
        findings=["Comparator analysis completed."],
        uncertainties=[],
        verification_items=[],
    )

    expected_summary = CasePreparationSummary(
        overview=(
            "Two analysis tasks completed successfully while evidence review "
            "remains incomplete."
        ),
        key_findings=[
            "Chronology analysis completed.",
            "Comparator analysis completed.",
        ],
        uncertainties=[],
        verification_items=[],
        incomplete_areas=[
            "T2 Evidence Review could not be completed."
        ],
    )

    orchestrator = Mock(return_value=execution_plan)

    def worker_side_effect(
        *,
        client,
        case_description,
        task,
    ) -> WorkerResult:
        del client, case_description

        if task.task_id == "T1":
            return worker_result_1

        if task.task_id == "T2":
            raise RuntimeError("Synthetic worker failure.")

        if task.task_id == "T3":
            return worker_result_3

        raise AssertionError(f"Unexpected task: {task.task_id}")

    worker = Mock(side_effect=worker_side_effect)
    synthesizer = Mock(return_value=expected_summary)

    monkeypatch.setattr(
        "workflow_engineering.workflows.legal_case_workflow."
        "create_execution_plan",
        orchestrator,
    )
    monkeypatch.setattr(
        "workflow_engineering.workflows.legal_case_workflow."
        "analyze_case_task",
        worker,
    )
    monkeypatch.setattr(
        "workflow_engineering.workflows.legal_case_workflow."
        "synthesize_case_preparation",
        synthesizer,
    )

    client = Mock()
    case_description = "Synthetic case for workflow coordination testing."

    result = await run_legal_case_workflow(
        client=client,
        case_description=case_description,
    )

    assert result.execution_plan == execution_plan
    assert result.case_preparation_summary == expected_summary
    assert len(result.worker_executions) == 3

    execution_1 = result.worker_executions[0]
    execution_2 = result.worker_executions[1]
    execution_3 = result.worker_executions[2]

    assert isinstance(execution_1, SuccessfulWorkerExecution)
    assert execution_1.task == task_1
    assert execution_1.result == worker_result_1

    assert isinstance(execution_2, FailedWorkerExecution)
    assert execution_2.task == task_2
    assert execution_2.error_type == "RuntimeError"
    assert execution_2.error_message == "Synthetic worker failure."

    assert isinstance(execution_3, SuccessfulWorkerExecution)
    assert execution_3.task == task_3
    assert execution_3.result == worker_result_3

    orchestrator.assert_called_once_with(
        client=client,
        case_description=case_description,
    )

    assert worker.call_count == 3

    synthesizer.assert_called_once_with(
        client=client,
        case_description=case_description,
        execution_plan=execution_plan,
        worker_executions=result.worker_executions,
    )