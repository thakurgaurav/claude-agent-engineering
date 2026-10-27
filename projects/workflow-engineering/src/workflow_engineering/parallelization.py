"""Parallelization and aggregation workflows using Claude tool use.

Author:
Gaurav Thakur

Description:
Demonstrates Claude parallel tool calling with application-managed concurrent
execution. Claude determines which independent travel intelligence tools are
required, the application executes those tools concurrently, and Claude
semantically aggregates successful results while being informed about
individual tool failures.
"""

import asyncio
import time
from typing import Any

from anthropic.types.beta import BetaMessageParam, BetaToolResultBlockParam
from claude_engineering.claude_client import create_claude_client
from claude_engineering.constants import CLAUDE_MODEL

from workflow_engineering.tools.travel_tools import (
    get_destination_air_quality,
    get_destination_weather,
    get_nearby_fire_activity,
)


def _extract_text(message: Any) -> str:
    """Extract text content from a Claude response."""
    text_blocks = [
        block.text
        for block in message.content
        if block.type == "text"
    ]

    if not text_blocks:
        raise RuntimeError(
            "Claude completed without returning a text response. "
            f"stop_reason={message.stop_reason}"
        )

    return "\n".join(text_blocks)


def run_parallel_travel_workflow_with_tool_runner(
    travel_request: str,
) -> str:
    """Run the travel workflow using the Anthropic SDK Tool Runner.

    Claude determines which tools are required. The Anthropic SDK manages
    tool execution, tool-result delivery, and subsequent Claude turns.

    This implementation is retained as a comparison with the manually
    orchestrated concurrent implementation below.
    """
    client = create_claude_client()

    runner = client.beta.messages.tool_runner(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        tools=[
            get_destination_weather,
            get_destination_air_quality,
            get_nearby_fire_activity,
        ],
        messages=[
            {
                "role": "user",
                "content": travel_request,
            }
        ],
    )

    final_message = runner.until_done()

    return _extract_text(final_message)


async def run_parallel_travel_workflow(
    travel_request: str,
) -> str:
    """Run the travel workflow with isolated concurrent tool execution.

    Claude selects the required tools in one model turn. Independent
    synchronous tools execute concurrently using worker threads.

    A failure in one tool does not discard successful results from the
    other tools. Successful and failed results are returned together to
    Claude for semantic aggregation.
    """
    workflow_start = time.perf_counter()

    client = create_claude_client()

    tools = [
        get_destination_weather.to_dict(),
        get_destination_air_quality.to_dict(),
        get_nearby_fire_activity.to_dict(),
    ]

    messages: list[BetaMessageParam] = [
        {
            "role": "user",
            "content": travel_request,
        }
    ]

    # Phase 1: Claude determines which tools should be executed.
    selection_start = time.perf_counter()

    response = client.beta.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        tools=tools,
        messages=messages,
    )

    selection_seconds = (
        time.perf_counter()
        - selection_start
    )

    tool_calls = [
        block
        for block in response.content
        if block.type == "tool_use"
    ]

    if not tool_calls:
        total_seconds = (
            time.perf_counter()
            - workflow_start
        )

        print(
            "\nWorkflow timing:"
            f"\n  Claude tool selection:   {selection_seconds:.2f}s"
            f"\n  Tool execution:          0.00s"
            f"\n  Claude aggregation:      0.00s"
            f"\n  Total:                   {total_seconds:.2f}s"
        )

        return _extract_text(response)

    print("\nClaude requested tools:")

    for tool_call in tool_calls:
        print(
            f"  - {tool_call.name}: "
            f"{tool_call.input}"
        )

    # Phase 2: Execute independent tools concurrently.
    available_tools = {
        "get_destination_weather": get_destination_weather,
        "get_destination_air_quality": get_destination_air_quality,
        "get_nearby_fire_activity": get_nearby_fire_activity,
    }

    tool_tasks = []

    for tool_call in tool_calls:
        tool = available_tools.get(tool_call.name)

        if tool is None:
            raise RuntimeError(
                f"Claude requested unsupported tool: {tool_call.name}"
            )

        tool_tasks.append(
            asyncio.to_thread(
                tool.call,
                tool_call.input,
            )
        )

    tool_start = time.perf_counter()

    tool_outputs = await asyncio.gather(
        *tool_tasks,
        return_exceptions=True,
    )

    tool_seconds = (
        time.perf_counter()
        - tool_start
    )

    # Phase 3: Build successful and failed tool results.
    tool_results: list[BetaToolResultBlockParam] = []

    for tool_call, output in zip(
        tool_calls,
        tool_outputs,
    ):
        if isinstance(output, BaseException):
            print(
                f"[TOOL ERROR] {tool_call.name}: "
                f"{type(output).__name__}: {output}"
            )

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": (
                        f"{tool_call.name} failed because an "
                        "external dependency was unavailable. "
                        f"Error type: {type(output).__name__}."
                    ),
                    "is_error": True,
                }
            )

            continue

        tool_results.append(
            {
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": str(output),
            }
        )

    # Preserve Claude's original tool-use response.
    messages.append(
        {
            "role": "assistant",
            "content": response.content,
        }
    )

    # Return every tool result together in one user message.
    messages.append(
        {
            "role": "user",
            "content": tool_results,
        }
    )

    # Phase 4: Claude aggregates both successes and failures.
    aggregation_start = time.perf_counter()

    final_response = client.beta.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        tools=tools,
        messages=messages,
    )

    aggregation_seconds = (
        time.perf_counter()
        - aggregation_start
    )

    total_seconds = (
        time.perf_counter()
        - workflow_start
    )

    print(
        "\nWorkflow timing:"
        f"\n  Claude tool selection:    {selection_seconds:.2f}s"
        f"\n  Parallel tool execution:  {tool_seconds:.2f}s"
        f"\n  Claude aggregation:       {aggregation_seconds:.2f}s"
        f"\n  Total:                    {total_seconds:.2f}s"
    )

    return _extract_text(final_response)
