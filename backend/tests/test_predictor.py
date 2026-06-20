import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.ml.predictor import Predictor

@pytest.mark.asyncio
async def test_predictor_returns_correct_structure():
    predictor = Predictor()
    mock_model = MagicMock()
    mock_model.predict.return_value = {
        "home_win": 0.54, "draw": 0.26, "away_win": 0.20, "confidence": "medium"
    }
    predictor._models = {"national": mock_model}

    result = predictor._run_model(
        competition_type="national",
        home_team="Brazil", away_team="France",
        home_strength=1823.0, away_strength=1756.0,
        home_history=[], away_history=[], h2h=[],
        stage="GROUP", days_rest=4,
    )
    assert result["home_win"] == 0.54
    assert "predicted_score" in result
    total = result["home_win"] + result["draw"] + result["away_win"]
    assert abs(total - 1.0) < 1e-6
