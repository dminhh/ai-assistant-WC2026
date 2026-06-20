import pytest
from unittest.mock import AsyncMock, patch, MagicMock, call
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_react_agent_streams_response():
    from app.agent.react_agent import run_react_agent

    mock_db = MagicMock()

    async def fake_stream_final(messages):
        yield "Hôm nay có 4 trận"

    with patch("app.agent.react_agent.openai_client") as mock_client, \
         patch("app.agent.react_agent._stream_final", new=fake_stream_final):

        # Mock first call: no tool calls, returns direct answer
        mock_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content="Hôm nay có 4 trận", tool_calls=None))]
            )
        )

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


def test_chat_endpoint_data_query():
    """POST /chat with data_query routes to react agent and streams SSE."""
    from app.main import app
    from app.database import get_db

    async def fake_get_db():
        yield MagicMock()

    async def fake_react_agent(question, db):
        yield "token1"
        yield "token2"

    with patch("app.routers.chat.classify_query", new=AsyncMock(return_value="data_query")), \
         patch("app.routers.chat.run_react_agent", side_effect=fake_react_agent):
        app.dependency_overrides[get_db] = fake_get_db
        client = TestClient(app)
        response = client.post("/chat", json={"message": "Hôm nay có trận nào?"})
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    content = response.text
    assert "data: token1\n\n" in content
    assert "data: token2\n\n" in content
    assert "data: [DONE]\n\n" in content


def test_chat_endpoint_analysis_query():
    """POST /chat with analysis_query routes to reflection agent and streams SSE."""
    from app.main import app
    from app.database import get_db

    async def fake_get_db():
        yield MagicMock()

    async def fake_reflection_agent(question, db):
        yield "analysis_token"

    with patch("app.routers.chat.classify_query", new=AsyncMock(return_value="analysis_query")), \
         patch("app.routers.chat.run_reflection_agent", side_effect=fake_reflection_agent):
        app.dependency_overrides[get_db] = fake_get_db
        client = TestClient(app)
        response = client.post("/chat", json={"message": "Brazil có thắng không?"})
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    content = response.text
    assert "data: analysis_token\n\n" in content
    assert "data: [DONE]\n\n" in content
