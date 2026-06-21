# app/schemas/match.py
from datetime import datetime
from pydantic import BaseModel


class MatchResponse(BaseModel):
    id: int
    competition_id: int
    home_team: str
    away_team: str
    kickoff_time: datetime
    status: str
    home_score: int | None
    away_score: int | None
    minute: int | None

    model_config = {"from_attributes": True}
