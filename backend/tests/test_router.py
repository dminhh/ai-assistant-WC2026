import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.agent.router import classify_query


@pytest.mark.asyncio
async def test_score_question_is_data_query():
    with patch("app.agent.router.openai_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="data_query"))]
        ))
        result = await classify_query("Tỉ số Brazil bao nhiêu?")
        assert result == "data_query"


@pytest.mark.asyncio
async def test_prediction_question_is_analysis_query():
    with patch("app.agent.router.openai_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="analysis_query"))]
        ))
        result = await classify_query("Brazil hay France sẽ thắng?")
        assert result == "analysis_query"


@pytest.mark.asyncio
async def test_invalid_response_defaults_to_analysis():
    with patch("app.agent.router.openai_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="something_unexpected"))]
        ))
        result = await classify_query("Câu hỏi phức tạp")
        assert result == "analysis_query"
