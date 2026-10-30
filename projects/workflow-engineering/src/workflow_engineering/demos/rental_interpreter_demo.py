"""Demo for the Claude rental requirement interpreter.

Author: Gaurav Thakur

Description:
Demonstrates interpreting a natural-language rental request.
"""

from claude_engineering.claude_client import create_claude_client

from workflow_engineering.interpreters.rental_requirement_interpreter import (
    RentalRequirementInterpreter,
)


def main() -> None:
    """Run the rental requirement interpreter demo."""
    client = create_claude_client()
    interpreter = RentalRequirementInterpreter(client)

    user_request = """
    I'm looking for a 2-bedroom apartment in San Jose.
    My absolute maximum is $3,500.

    I have a dog, so pets must be allowed, and I need parking.

    Safety is extremely important.
    I'd prefer something newer and spacious, but I would take an older
    or slightly smaller apartment if it is significantly safer.

    In-unit laundry is important.
    A gym is nice but doesn't really matter.

    I would also like a quiet neighborhood.
    """

    intent = interpreter.interpret(user_request)

    print(intent)


if __name__ == "__main__":
    main()
