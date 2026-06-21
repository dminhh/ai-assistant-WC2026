from datetime import datetime
from pydantic import BaseModel


class PredictionResponse(BaseModel):
    id: int
    match_id: int
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    predicted_score: str | None
    score_probs: list | None
    confidence: str
    model_version: str
    created_at: datetime

    model_config = {"from_attributes": True}
