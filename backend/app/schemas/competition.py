# app/schemas/competition.py
from pydantic import BaseModel


class CompetitionResponse(BaseModel):
    id: int
    name: str
    api_competition_id: str
    is_active: bool
    country: str | None
    season: str | None
    logo_url: str | None

    model_config = {"from_attributes": True}
