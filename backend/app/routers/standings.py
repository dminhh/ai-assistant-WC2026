# app/routers/standings.py
from fastapi import APIRouter
from app.services.football_data import FootballDataClient
from app.config import get_settings

router = APIRouter(prefix="/standings", tags=["standings"])


@router.get("/{competition_id}")
async def get_standings(competition_id: str):
    client = FootballDataClient(api_key=get_settings().football_data_api_key)
    return await client.get_standings(competition_id)
