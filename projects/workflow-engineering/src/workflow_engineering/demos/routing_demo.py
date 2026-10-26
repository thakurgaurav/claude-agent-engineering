"""Runnable demonstration of the decision-routing workflow.

Author:
    Gaurav Thakur
Description:
    Demonstrates routing a sample decision and generating its route-specific
    plan.
"""

from workflow_engineering.routing import run_routing_workflow

DECISION_REQUEST = """
I am deciding whether to reorganize my weekly personal schedule.
I want more uninterrupted time for important tasks while still keeping
enough flexibility for unexpected responsibilities.
""".strip()

DECISION_REQUEST1 = """
I am planning a one-week vacation and deciding between destinations.
I want a place with good weather, reasonable overall cost, and activities
suitable for a family.
""".strip()



DECISION_REQUEST2 = """
I need a laptop under $1,500 for Java development, AI experimentation,
and occasional video editing. Battery life is important and I want to
keep it for at least five years.
""".strip()

DECISION_REQUEST3 = """
I am considering an AI certification to strengthen my skills and improve
my long-term career opportunities. I want to understand whether the time
and cost required would provide enough professional value.
""".strip()

def main() -> None:
    """Run the routing workflow demonstration."""
    route, plan = run_routing_workflow(DECISION_REQUEST)

    print("\n=== ROUTING WORKFLOW RESULT ===\n")
    print(f"Selected route: {route.value}")
    print("\n=== ROUTE-SPECIFIC PLAN ===\n")
    print(plan)


if __name__ == "__main__":
    main()
