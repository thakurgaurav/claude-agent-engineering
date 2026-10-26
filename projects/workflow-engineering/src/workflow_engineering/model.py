"""Shared Claude client and model invocation utilities.

Author:
    Gaurav Thakur
Description:
    Provides the configured Claude client and a reusable function for sending
    prompts with consistent inference settings and response handling.
"""

from anthropic import Anthropic
from claude_engineering.config import get_anthropic_api_key
from claude_engineering.constants import CLAUDE_MODEL

_client: Anthropic | None = None


def get_claude_client() -> Anthropic:
    """Return the process-level Claude API client, creating it when first needed."""
    global _client

    if _client is None:
        _client = Anthropic(api_key=get_anthropic_api_key())

    return _client


def call_model(
    prompt: str,
    *,
    max_tokens: int = 600,
    thinking_enabled: bool = False,
    effort: str = "low",
) -> str:
    """Send a prompt to Claude using configurable inference settings."""
    client = get_claude_client()

    kwargs = {
        "model": CLAUDE_MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }

    if not thinking_enabled:
        kwargs["thinking"] = {"type": "disabled"}

    response = client.messages.create(**kwargs)


    text_blocks = [
        block.text
        for block in response.content
        if block.type == "text"
    ]

    if not text_blocks:
      raise RuntimeError(
        f"Claude response contained no text. "
        f"stop_reason={response.stop_reason}"
    )

    if response.stop_reason == "max_tokens":
      raise RuntimeError(
        f"Claude response was truncated after "
        f"{response.usage.output_tokens} output tokens."
    )


    return "\n".join(text_blocks)
