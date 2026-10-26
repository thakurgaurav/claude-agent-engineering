"""Utilities for loading packaged prompt templates.

Author:
    Gaurav Thakur
Description:
    Loads prompt resources from the workflow-engineering package.
"""

from importlib.resources import files

PROMPT_PACKAGE = "workflow_engineering.prompts"


def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from the packaged prompt resources.

    Args:
        prompt_name: Name of the prompt resource file.

    Returns:
        The prompt template as text.
    """
    return (
        files(PROMPT_PACKAGE)
        .joinpath(prompt_name)
        .read_text(encoding="utf-8")
        .strip()
    )
