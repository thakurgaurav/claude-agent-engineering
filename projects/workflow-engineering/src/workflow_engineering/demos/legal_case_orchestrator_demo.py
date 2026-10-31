"""Demo for the legal case preparation orchestrator.

Author: Gaurav Thakur

Description:
Runs synthetic legal cases of different types and complexity through the
orchestrator to demonstrate dynamic execution-plan generation.

This demo is for educational purposes only and does not provide legal advice.
"""

from claude_engineering.claude_client import create_claude_client

from workflow_engineering.orchestrators.legal_case_orchestrator import (
    create_execution_plan,
)

SYNTHETIC_CASES = {
    "Simple security deposit dispute": """
        My landlord has not returned my security deposit after I moved out.
        I have the lease and proof that I paid the deposit.
    """,
    "Complex landlord dispute": """
        I rented an apartment and paid a $2,500 security deposit.

        I gave my landlord written notice before moving out and returned the
        keys on the agreed move-out date. More than a month has passed, but my
        security deposit has not been returned.

        The landlord says part of the deposit is being withheld because of
        damage to the apartment and also claims that I owe additional rent.

        I have the original lease, proof of my rent payments, emails exchanged
        with the landlord, a copy of my move-out notice, and photographs taken
        when I moved out showing the condition of the apartment.

        I want to understand what issues should be analyzed and what
        information would be important when preparing this matter for further
        review.
    """,
    "Employment termination dispute": """
        I was terminated from my job for what my employer described as poor
        performance.

        My recent performance reviews were positive, and I have emails from my
        manager praising my work shortly before the termination.

        I have copies of my performance reviews, relevant emails, and the
        termination letter. I want to understand what issues and evidence
        should be analyzed before I discuss the matter with an attorney.
    """,
    "Test worker number": """I paid my landlord a $1,500 security deposit. I moved out two months ago, and the landlord has not returned the deposit or contacted me about any deductions.

    I only want to understand what should be analyzed regarding the unreturned security deposit.
""",
}


def main() -> None:
    """Generate and display execution plans for synthetic legal cases."""
    client = create_claude_client()

    for case_name, case_description in SYNTHETIC_CASES.items():
        plan = create_execution_plan(
            client=client,
            case_description=case_description,
        )

        print("\n")
        print("=" * 72)
        print(case_name)
        print("=" * 72)

        for task in plan.tasks:
            print(f"\n[{task.task_id}] {task.title}")
            print(f"Objective: {task.objective}")

        print(f"\nTotal tasks: {len(plan.tasks)}")


if __name__ == "__main__":
    main()