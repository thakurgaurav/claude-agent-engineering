"""Demo for a single legal case-analysis worker.

Author: Gaurav Thakur

Description:
Executes one predefined case-analysis task against a synthetic legal case to
verify the worker contract independently from orchestration and concurrency.

This demo is for educational purposes only and does not provide legal advice.
"""

from claude_engineering.claude_client import create_claude_client

from workflow_engineering.orchestrators.legal_case_orchestrator import CaseTask
from workflow_engineering.workers.legal_case_worker import analyze_case_task

SYNTHETIC_CASE = """
I rented an apartment and paid a $2,500 security deposit.

I moved out more than a month ago after giving written notice and returning
the keys. The landlord has not returned the full deposit and says that part
of it is being withheld because of damage to the apartment.

I have the original lease, my move-out notice, email exchanges with the
landlord, and photographs taken when I moved out showing the condition of
the apartment.
""".strip()

SYNTHETIC_TASK = CaseTask(
    task_id="T1",
    title="Security deposit damage deduction analysis",
    objective=(
        "Analyze the landlord's stated damage-related reason for withholding "
        "part of the security deposit. Consider the available evidence, "
        "identify important missing information, and identify legal matters "
        "that would require verification."
    ),
)


def main() -> None:
    """Execute and display the result of one case-analysis worker."""
    client = create_claude_client()

    result = analyze_case_task(
        client=client,
        case_description=SYNTHETIC_CASE,
        task=SYNTHETIC_TASK,
    )

    print("\nWorker result")
    print("=" * 72)
    print(f"Task: {result.task_id}")

    print("\nFindings")
    for finding in result.findings:
        print(f"- {finding}")

    print("\nUncertainties")
    for uncertainty in result.uncertainties:
        print(f"- {uncertainty}")

    print("\nVerification required")
    for item in result.verification_items:
        print(f"- {item}")


if __name__ == "__main__":
    main()