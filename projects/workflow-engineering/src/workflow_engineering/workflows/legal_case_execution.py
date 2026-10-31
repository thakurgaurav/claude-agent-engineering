"""Execution contracts for the legal case preparation workflow.

Author: Gaurav Thakur

Description:
Defines shared execution-result contracts used to represent successful and
failed legal case worker executions. These contracts are shared by workflow
coordination and downstream synthesis.
"""

from pydantic import BaseModel

from workflow_engineering.orchestrators.legal_case_orchestrator import CaseTask
from workflow_engineering.workers.legal_case_worker import WorkerResult


class SuccessfulWorkerExecution(BaseModel):
    """Successful execution of one orchestrator-generated task."""

    task: CaseTask
    result: WorkerResult


class FailedWorkerExecution(BaseModel):
    """Failed execution of one orchestrator-generated task."""

    task: CaseTask
    error_type: str
    error_message: str


WorkerExecution = SuccessfulWorkerExecution | FailedWorkerExecution