"""Utilities for reliable Claude structured-output calls.

Author: Gaurav Thakur

Description:
Provides validated structured-output calls with a single repair attempt.
"""

from anthropic import Anthropic
from claude_engineering.constants import CLAUDE_MODEL
from pydantic import BaseModel, ValidationError

_MAX_STRUCTURED_OUTPUT_ATTEMPTS = 2


def call_structured_tool[OutputT: BaseModel](
    *,
    client: Anthropic,
    system_prompt: str,
    user_message: str,
    tool_name: str,
    tool_description: str,
    output_model: type[OutputT],
    max_tokens: int,
) -> OutputT:
    """Call Claude and return validated structured tool output.

    Claude receives one repair attempt when it returns malformed structured
    output. API and transport failures are intentionally not retried here.

    Raises:
        RuntimeError: If Claude does not produce valid structured output
            after the configured number of attempts.
    """
    validation_errors: list[str] = []

    for attempt in range(1, _MAX_STRUCTURED_OUTPUT_ATTEMPTS + 1):
        message = user_message

        if attempt > 1:
            message = _build_repair_message(
                original_message=user_message,
                output_model=output_model,
                previous_error=validation_errors[-1],
            )

        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            tools=[
                {
                    "type": "custom",
                    "name": tool_name,
                    "description": tool_description,
                    "input_schema": output_model.model_json_schema(),
                }
            ],
            tool_choice={
                "type": "tool",
                "name": tool_name,
            },
        )

        tool_uses = [
            block
            for block in response.content
            if block.type == "tool_use"
            and block.name == tool_name
        ]

        if len(tool_uses) != 1:
            validation_errors.append(
                f"Attempt {attempt}: expected exactly one "
                f"{tool_name!r} tool call but received "
                f"{len(tool_uses)}."
            )
            continue

        tool_input = tool_uses[0].input

        try:
            return output_model.model_validate(tool_input)
        except ValidationError as exc:
            validation_errors.append(
                f"Attempt {attempt}: invalid tool input "
                f"{tool_input!r}. Validation error: {exc}"
            )

    details = "\n".join(validation_errors)

    raise RuntimeError(
        f"Claude failed to produce valid structured output for tool "
        f"{tool_name!r} after "
        f"{_MAX_STRUCTURED_OUTPUT_ATTEMPTS} attempts.\n"
        f"{details}"
    )


def _build_repair_message(
    *,
    original_message: str,
    output_model: type[BaseModel],
    previous_error: str,
) -> str:
    """Build a repair request containing the original task and contract."""
    schema = output_model.model_json_schema()

    return (
        f"{original_message}\n\n"
        "STRUCTURED OUTPUT REPAIR REQUIRED\n"
        "Your previous tool input failed application validation.\n\n"
        f"Validation failure:\n{previous_error}\n\n"
        "Call the required tool again and provide a COMPLETE tool input.\n"
        "Do not return only the corrected field.\n"
        "Do not omit required fields from the schema.\n\n"
        f"Required JSON schema:\n{schema}\n\n"
        "Return all required fields in the tool call."
    )
