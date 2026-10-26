from claude_engineering.claude_client import create_claude_client
from claude_engineering.constants import CLAUDE_MODEL


def test_claude_connection() -> None:
    client = create_claude_client()

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=20,
        thinking={"type": "disabled"},
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: Claude connection successful",
            }
        ],
    )

    text_blocks = [
        block.text
        for block in response.content
        if block.type == "text"
    ]

    assert text_blocks
    assert "Claude connection successful" in "\n".join(text_blocks)
