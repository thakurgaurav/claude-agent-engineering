"""Shared configuration helpers for Claude integrations.

Author:
    Gaurav Thakur
Description:
    Loads and validates the Anthropic API key from environment variables.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def get_anthropic_api_key() -> str:
    """Return the configured Anthropic API key."""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    return api_key
