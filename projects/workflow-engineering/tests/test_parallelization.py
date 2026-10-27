"""Tests for parallel travel workflow orchestration.

Author:
Gaurav Thakur

Description:
Verifies Claude tool selection, concurrent tool-result handling,
semantic aggregation, graceful degradation, and direct-response behavior
without calling live Claude or external provider APIs.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from workflow_engineering import parallelization


def _text_block(text: str) -> SimpleNamespace:
    """Create a Claude-like text content block."""
    return SimpleNamespace(
        type="text",
        text=text,
    )


def _tool_use_block(
    tool_id: str,
    name: str,
    tool_input: dict[str, str],
) -> SimpleNamespace:
    """Create a Claude-like tool-use content block."""
    return SimpleNamespace(
        type="tool_use",
        id=tool_id,
        name=name,
        input=tool_input,
    )


def _message(
    content: list[SimpleNamespace],
    stop_reason: str = "end_turn",
) -> SimpleNamespace:
    """Create a Claude-like response message."""
    return SimpleNamespace(
        content=content,
        stop_reason=stop_reason,
    )


@pytest.mark.asyncio
async def test_parallel_workflow_executes_multiple_tools_and_aggregates(
    monkeypatch,
) -> None:
    """Execute all Claude-requested tools and aggregate their results."""
    selection_response = _message(
        [
            _tool_use_block(
                "tool-weather",
                "get_destination_weather",
                {
                    "destination": "Los Angeles",
                    "travel_date": "2026-10-30",
                },
            ),
            _tool_use_block(
                "tool-air-quality",
                "get_destination_air_quality",
                {
                    "destination": "Los Angeles",
                    "travel_date": "2026-10-30",
                },
            ),
            _tool_use_block(
                "tool-fire",
                "get_nearby_fire_activity",
                {
                    "destination": "Los Angeles",
                },
            ),
        ]
    )

    aggregation_response = _message(
        [
            _text_block(
                "Conditions are generally suitable with some caution."
            )
        ]
    )

    mock_create = Mock(
        side_effect=[
            selection_response,
            aggregation_response,
        ]
    )

    mock_client = SimpleNamespace(
        beta=SimpleNamespace(
            messages=SimpleNamespace(
                create=mock_create,
            )
        )
    )

    monkeypatch.setattr(
        parallelization,
        "create_claude_client",
        lambda: mock_client,
    )

    monkeypatch.setattr(
        parallelization.get_destination_weather,
        "call",
        Mock(return_value="Weather result"),
    )

    monkeypatch.setattr(
        parallelization.get_destination_air_quality,
        "call",
        Mock(return_value="Air-quality result"),
    )

    monkeypatch.setattr(
        parallelization.get_nearby_fire_activity,
        "call",
        Mock(return_value="Fire-activity result"),
    )

    result = await parallelization.run_parallel_travel_workflow(
        "Check Los Angeles travel conditions."
    )

    assert result == (
        "Conditions are generally suitable with some caution."
    )

    assert mock_create.call_count == 2

    final_call = mock_create.call_args_list[1]
    final_messages = final_call.kwargs["messages"]

    tool_result_message = final_messages[-1]

    assert tool_result_message["role"] == "user"

    tool_results = tool_result_message["content"]

    assert len(tool_results) == 3

    assert tool_results[0]["tool_use_id"] == "tool-weather"
    assert tool_results[0]["content"] == "Weather result"

    assert tool_results[1]["tool_use_id"] == "tool-air-quality"
    assert tool_results[1]["content"] == "Air-quality result"

    assert tool_results[2]["tool_use_id"] == "tool-fire"
    assert tool_results[2]["content"] == "Fire-activity result"


@pytest.mark.asyncio
async def test_parallel_workflow_isolates_tool_failure(
    monkeypatch,
) -> None:
    """Preserve successful tool results when one parallel tool fails."""
    selection_response = _message(
        [
            _tool_use_block(
                "tool-weather",
                "get_destination_weather",
                {
                    "destination": "Los Angeles",
                    "travel_date": "2026-10-30",
                },
            ),
            _tool_use_block(
                "tool-air-quality",
                "get_destination_air_quality",
                {
                    "destination": "Los Angeles",
                    "travel_date": "2026-10-30",
                },
            ),
            _tool_use_block(
                "tool-fire",
                "get_nearby_fire_activity",
                {
                    "destination": "Los Angeles",
                },
            ),
        ]
    )

    aggregation_response = _message(
        [
            _text_block(
                "Assessment produced using the available evidence."
            )
        ]
    )

    mock_create = Mock(
        side_effect=[
            selection_response,
            aggregation_response,
        ]
    )

    mock_client = SimpleNamespace(
        beta=SimpleNamespace(
            messages=SimpleNamespace(
                create=mock_create,
            )
        )
    )

    monkeypatch.setattr(
        parallelization,
        "create_claude_client",
        lambda: mock_client,
    )

    monkeypatch.setattr(
        parallelization.get_destination_weather,
        "call",
        Mock(return_value="Weather result"),
    )

    monkeypatch.setattr(
        parallelization.get_destination_air_quality,
        "call",
        Mock(side_effect=TimeoutError("provider timeout")),
    )

    monkeypatch.setattr(
        parallelization.get_nearby_fire_activity,
        "call",
        Mock(return_value="Fire-activity result"),
    )

    result = await parallelization.run_parallel_travel_workflow(
        "Check Los Angeles travel conditions."
    )

    assert result == (
        "Assessment produced using the available evidence."
    )

    final_call = mock_create.call_args_list[1]
    final_messages = final_call.kwargs["messages"]

    tool_results = final_messages[-1]["content"]

    assert len(tool_results) == 3

    weather_result = tool_results[0]
    air_quality_result = tool_results[1]
    fire_result = tool_results[2]

    assert weather_result["content"] == "Weather result"

    assert air_quality_result["tool_use_id"] == "tool-air-quality"
    assert air_quality_result["is_error"] is True
    assert "TimeoutError" in air_quality_result["content"]

    assert fire_result["content"] == "Fire-activity result"


@pytest.mark.asyncio
async def test_parallel_workflow_returns_direct_response_when_no_tools_requested(
    monkeypatch,
) -> None:
    """Return Claude text directly when Claude does not request tools."""
    direct_response = _message(
        [
            _text_block(
                "No external travel information is required."
            )
        ]
    )

    mock_create = Mock(
        return_value=direct_response,
    )

    mock_client = SimpleNamespace(
        beta=SimpleNamespace(
            messages=SimpleNamespace(
                create=mock_create,
            )
        )
    )

    monkeypatch.setattr(
        parallelization,
        "create_claude_client",
        lambda: mock_client,
    )

    result = await parallelization.run_parallel_travel_workflow(
        "Say hello."
    )

    assert result == "No external travel information is required."

    # No aggregation call should occur.
    assert mock_create.call_count == 1


@pytest.mark.asyncio
async def test_parallel_workflow_rejects_unsupported_tool(
    monkeypatch,
) -> None:
    """Reject a tool request that is not exposed by the application."""
    selection_response = _message(
        [
            _tool_use_block(
                "tool-unknown",
                "delete_everything",
                {},
            )
        ]
    )

    mock_create = Mock(
        return_value=selection_response,
    )

    mock_client = SimpleNamespace(
        beta=SimpleNamespace(
            messages=SimpleNamespace(
                create=mock_create,
            )
        )
    )

    monkeypatch.setattr(
        parallelization,
        "create_claude_client",
        lambda: mock_client,
    )

    with pytest.raises(
        RuntimeError,
        match="Claude requested unsupported tool",
    ):
        await parallelization.run_parallel_travel_workflow(
            "Run an unsupported capability."
        )