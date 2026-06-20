import pytest
from unittest.mock import AsyncMock, patch, MagicMock, call


@pytest.mark.asyncio
async def test_react_agent_streams_response():
    from app.agent.react_agent import run_react_agent

    mock_db = MagicMock()

    with patch("app.agent.react_agent.openai_client") as mock_client, \
         patch("app.agent.react_agent._stream_final") as mock_stream_final:

        # Mock first call: no tool calls, returns direct answer
        mock_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content="Hôm nay có 4 trận", tool_calls=None))]
            )
        )

        # Mock _stream_final to yield tokens directly
        async def fake_stream_final(messages):
            yield "Hôm nay có 4 trận"

        mock_stream_final.side_effect = fake_stream_final

        tokens = []
        async for token in run_react_agent("Hôm nay có trận nào?", db=mock_db):
            tokens.append(token)

        assert len(tokens) > 0
        assert "".join(tokens) == "Hôm nay có 4 trận"


@pytest.mark.asyncio
async def test_reflection_agent_streams_response():
    from app.agent.reflection_agent import run_reflection_agent

    mock_db = MagicMock()

    # Non-streaming response mock (for collect/draft/critique phases)
    non_stream_response = MagicMock(
        choices=[MagicMock(
            message=MagicMock(
                content="Brazil có 54% xác suất thắng",
                tool_calls=None,
            ),
            finish_reason="stop",
        )]
    )

    # Streaming chunk mocks (for stream phase)
    chunk1 = MagicMock(choices=[MagicMock(delta=MagicMock(content="Brazil "))])
    chunk2 = MagicMock(choices=[MagicMock(delta=MagicMock(content="sẽ thắng!"))])

    async def fake_aiter(self):
        yield chunk1
        yield chunk2

    mock_stream = MagicMock()
    mock_stream.__aiter__ = fake_aiter

    call_count = 0

    async def fake_create(**kwargs):
        nonlocal call_count
        call_count += 1
        if kwargs.get("stream"):
            return mock_stream
        return non_stream_response

    with patch("app.agent.reflection_agent.openai_client") as mock_client:
        mock_client.chat.completions.create = fake_create

        tokens = []
        async for token in run_reflection_agent("Brazil có thắng không?", db=mock_db):
            tokens.append(token)

    assert len(tokens) > 0
    assert "".join(tokens) == "Brazil sẽ thắng!"
