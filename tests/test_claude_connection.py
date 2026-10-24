from claude_agent_engineering.common.claude_client import create_claude_client


def test_claude_connection() -> None:
    client = create_claude_client()

    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=20,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: Claude connection successful",
            }
        ],
    )

    print(response.content[0].text)