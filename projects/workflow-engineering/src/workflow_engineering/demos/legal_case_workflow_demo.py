"""Demonstration of the legal case orchestrator-worker workflow.

Author: Gaurav Thakur

Description:
Runs a synthetic legal case through dynamic task planning, concurrent worker
analysis, failure isolation, and final synthesis.

This demonstration is educational only. It does not provide legal advice and
does not use authoritative or guaranteed-current legal sources.
"""

import asyncio

from claude_engineering.claude_client import create_claude_client

from workflow_engineering.workflows.legal_case_execution import (
    FailedWorkerExecution,
    SuccessfulWorkerExecution,
)
from workflow_engineering.workflows.legal_case_workflow import (
    run_legal_case_workflow,
)

SYNTHETIC_CASE = """
I worked for a software company for three years and was recently terminated.

About two months before my termination, I reported concerns to my manager and
HR that employees on my team were regularly working additional hours that were
not appearing in the company's time records.

Before I raised these concerns, my performance reviews had generally been
positive. After I reported the issue, my manager began giving me negative
feedback. About three weeks later, I was placed on a performance improvement
plan. Approximately six weeks after that, the company terminated my employment
for poor performance.

I have copies of my previous performance reviews, the performance improvement
plan, emails with my manager and HR about the working-hours issue, some team
messages discussing working hours, and my termination letter.

I do not know whether other employees raised similar concerns or whether anyone
else was disciplined or terminated.

I want to understand what issues should be analyzed, what evidence is important,
what information is missing, and what matters would require verification before
this situation is reviewed further.
""".strip()


def _print_list(items: list[str]) -> None:
    """Print a list of strings in a readable format."""
    if not items:
        print("- None")
        return

    for item in items:
        print(f"- {item}")


async def main() -> None:
    """Run and display the complete legal case preparation workflow."""
    client = create_claude_client()

    result = await run_legal_case_workflow(
        client=client,
        case_description=SYNTHETIC_CASE,
    )

    print("\n" + "=" * 72)
    print("Execution plan")
    print("=" * 72)

    for task in result.execution_plan.tasks:
        print(f"\n[{task.task_id}] {task.title}")
        print(f"Objective: {task.objective}")

    print("\n\n" + "=" * 72)
    print("Worker executions")
    print("=" * 72)

    successful_count = 0
    failed_count = 0

    for execution in result.worker_executions:
        print(
            f"\n[{execution.task.task_id}] "
            f"{execution.task.title}"
        )

        if isinstance(execution, SuccessfulWorkerExecution):
            successful_count += 1
            print("Status: SUCCESS")

            print("\nFindings")
            _print_list(execution.result.findings)

            print("\nUncertainties")
            _print_list(execution.result.uncertainties)

            print("\nVerification required")
            _print_list(execution.result.verification_items)
            continue

        if isinstance(execution, FailedWorkerExecution):
            failed_count += 1
            print("Status: FAILED")
            print(f"Error type: {execution.error_type}")
            print(f"Error: {execution.error_message}")
            continue

        raise TypeError(
            "Unsupported worker execution type: "
            f"{type(execution).__name__}"
        )

    summary = result.case_preparation_summary

    print("\n\n" + "=" * 72)
    print("Case preparation summary")
    print("=" * 72)

    print("\nOverview")
    print(summary.overview)

    print("\nKey findings")
    _print_list(summary.key_findings)

    print("\nUncertainties")
    _print_list(summary.uncertainties)

    print("\nVerification required")
    _print_list(summary.verification_items)

    print("\nIncomplete areas")
    _print_list(summary.incomplete_areas)

    print("\n\n" + "=" * 72)
    print("Execution summary")
    print("=" * 72)
    print(f"Planned tasks: {len(result.execution_plan.tasks)}")
    print(f"Successful:    {successful_count}")
    print(f"Failed:        {failed_count}")


if __name__ == "__main__":
    asyncio.run(main())