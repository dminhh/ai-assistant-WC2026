# app/schemas/competition.py
from pydantic import BaseModel


class CompetitionCreate(BaseModel):
    name: str
    api_competition_id: str
    is_active: bool = False
    competition_type: str = "national"
    country: str | None = None
    season: str | None = None
    logo_url: str | None = None


class CompetitionResponse(BaseModel):
    id: int
    name: str
    api_competition_id: str
    is_active: bool
    country: str | None
    season: str | None
    logo_url: str | None

    model_config = {"from_attributes": True}
