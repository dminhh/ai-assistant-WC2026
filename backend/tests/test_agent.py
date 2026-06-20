import pytest
from unittest.mock import AsyncMock, patch, MagicMock


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
