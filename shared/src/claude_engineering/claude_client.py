from anthropic import Anthropic

from claude_engineering.config import get_anthropic_api_key


def create_claude_client() -> Anthropic:
    return Anthropic(api_key=get_anthropic_api_key())