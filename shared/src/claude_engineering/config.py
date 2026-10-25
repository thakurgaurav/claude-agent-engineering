import os

from dotenv import load_dotenv

load_dotenv()


def get_anthropic_api_key() -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    return api_key