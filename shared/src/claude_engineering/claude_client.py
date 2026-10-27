"""Factory functions for creating configured Claude clients.

Author:
    Gaurav Thakur
Description:
    Creates Anthropic clients using the shared API-key configuration.
"""

from anthropic import Anthropic

from claude_engineering.config import get_anthropic_api_key


def create_claude_client() -> Anthropic:
    """Create an Anthropic client configured with the application API key."""
    return Anthropic(api_key=get_anthropic_api_key())
