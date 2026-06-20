import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from app.agent.tools import get_today_fixtures, get_prediction, get_live_scores, get_standings, get_team_stats, get_h2h


@pytest.mark.asyncio
async def test_get_today_fixtures_returns_json(db_session):
    result = await get_today_fixtures(db=db_session)
    data = json.loads(result)
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_prediction_returns_probabilities():
    # Build a mock db and a mock match so the predictor path is exercised.
    mock_match = MagicMock()
    mock_match.id = 1

    mock_db = AsyncMock()
    mock_db.scalar.return_value = mock_match

    with patch("app.agent.tools.get_predictor") as mock_pred:
        predictor = MagicMock()
        predictor.predict_match = AsyncMock(return_value={
            "home_win": 0.54, "draw": 0.26, "away_win": 0.20,
            "predicted_score": "2-1", "confidence": "medium"
        })
        mock_pred.return_value = predictor

        result = await get_prediction(home_team="Brazil", away_team="France", db=mock_db)
        data = json.loads(result)
        assert "home_win" in data
        assert data["home_win"] == 0.54


@pytest.mark.asyncio
async def test_get_live_scores_returns_json(db_session):
    result = await get_live_scores(db=db_session)
    data = json.loads(result)
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_standings_competition_not_found():
    mock_db = AsyncMock()
    mock_db.scalar.return_value = None  # competition not found
    result = await get_standings(competition_name="Unknown League", db=mock_db)
    data = json.loads(result)
    assert "error" in data


@pytest.mark.asyncio
async def test_get_team_stats_returns_json():
    mock_db = AsyncMock()
    # Mock execute returning empty result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    result = await get_team_stats(team_name="Brazil", db=mock_db)
    data = json.loads(result)
    assert "team" in data
    assert "last_5" in data
    assert data["team"] == "Brazil"


@pytest.mark.asyncio
async def test_get_h2h_returns_json():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    result = await get_h2h(team_a="Brazil", team_b="France", db=mock_db)
    data = json.loads(result)
    assert isinstance(data, list)
