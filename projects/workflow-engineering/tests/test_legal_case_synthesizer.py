"""Tests for legal case preparation synthesis.

Author: Gaurav Thakur

Description:
Verifies that the legal case synthesizer preserves worker-failure visibility
and does not silently replace missing worker analysis.
"""

from unittest.mock import Mock

from workflow_engineering.orchestrators.legal_case_orchestrator import (
    CaseTask,
    ExecutionPlan,
)
from workflow_engineering.synthesizers.legal_case_synthesizer import (
    CasePreparationSummary,
    synthesize_case_preparation,
)
from workflow_engineering.workers.legal_case_worker import WorkerResult
from workflow_engineering.workflows.legal_case_execution import (
    FailedWorkerExecution,
    SuccessfulWorkerExecution,
)


def test_synthesizer_preserves_failed_worker_as_incomplete_area(
    monkeypatch,
) -> None:
    """Ensure failed worker analysis remains explicitly incomplete."""
    task_1 = CaseTask(
        task_id="T1",
        title="Chronology Analysis",
        objective="Analyze the sequence and timing of relevant events.",
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

    worker_executions = [
        SuccessfulWorkerExecution(
            task=task_1,
            result=WorkerResult(
                task_id="T1",
                findings=[
                    "The reported concern preceded the later employment actions."
                ],
                uncertainties=[
                    "Exact dates have not yet been confirmed."
                ],
                verification_items=[
                    "Confirm event dates against the available records."
                ],
            ),
        ),
        SuccessfulWorkerExecution(
            task=task_2,
            result=WorkerResult(
                task_id="T2",
                findings=[
                    (
                        "Performance reviews and the termination letter require "
                        "cross-document comparison."
                    )
                ],
                uncertainties=[
                    "The complete document contents are not available."
                ],
                verification_items=[
                    "Verify document completeness and authenticity."
                ],
            ),
        ),
        FailedWorkerExecution(
            task=task_3,
            error_type="RuntimeError",
            error_message="Synthetic worker failure.",
        ),
    ]

    expected_summary = CasePreparationSummary(
        overview=(
            "Available analysis covers chronology and documentary evidence, "
            "while comparator analysis remains incomplete."
        ),
        key_findings=[
            "The reported concern preceded the later employment actions.",
            (
                "Performance reviews and the termination letter require "
                "cross-document comparison."
            ),
        ],
        uncertainties=[
            "Exact dates have not yet been confirmed.",
            "The complete document contents are not available.",
        ],
        verification_items=[
            "Confirm event dates against the available records.",
            "Verify document completeness and authenticity.",
        ],
        incomplete_areas=[
            "T3 Comparator Analysis could not be completed because its worker failed."
        ],
    )

    structured_call = Mock(return_value=expected_summary)

    monkeypatch.setattr(
        "workflow_engineering.synthesizers.legal_case_synthesizer."
        "call_structured_tool",
        structured_call,
    )

    client = Mock()

    result = synthesize_case_preparation(
        client=client,
        case_description=(
            "Synthetic employment case used to test synthesis behavior."
        ),
        execution_plan=execution_plan,
        worker_executions=worker_executions,
    )

    assert result == expected_summary
    assert result.incomplete_areas
    assert "T3" in result.incomplete_areas[0]
    assert "Comparator Analysis" in result.incomplete_areas[0]

    structured_call.assert_called_once()

    call_arguments = structured_call.call_args.kwargs
    synthesis_message = call_arguments["user_message"]

    assert '"task_id": "T1"' in synthesis_message
    assert '"task_id": "T2"' in synthesis_message
    assert '"task_id": "T3"' in synthesis_message
    assert '"error_type": "RuntimeError"' in synthesis_message
    assert '"error_message": "Synthetic worker failure."' in synthesis_message
