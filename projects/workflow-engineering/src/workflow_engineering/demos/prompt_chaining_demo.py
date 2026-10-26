"""Runnable demonstration of the prompt-chaining workflow.

Author:
    Gaurav Thakur
Description:
    Demonstrates the multi-stage decision-analysis prompt chain.
"""

from workflow_engineering.prompt_chain import run_prompt_chain

DECISION_REQUEST1 = """
I need a laptop under $1,500 for Java development, AI experimentation,
and occasional video editing. Battery life is important and I want to
keep it for at least five years.
""".strip()

DECISION_REQUEST2 = """
I need to plan 7 days trip to Hawaii with my family. 
We want to visit the beaches, go hiking, water sports, enjoy in the nature.
As family includes 2 adults and 3 kids, we need to find a family-friendly accommodation.
With little kids, we dont want a hectic schedule, it should be relaxing. 
Looking for some good package deals which includes accommodation, sightseeing and activities.
""".strip()


def main() -> None:
    """Run the prompt-chaining demonstration."""
    research_plan = run_prompt_chain(DECISION_REQUEST1)

    print("\n=== PROMPT CHAINING RESULT ===\n")
    print(research_plan)


if __name__ == "__main__":
    main()
