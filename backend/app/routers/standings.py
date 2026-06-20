# app/routers/standings.py
from typing import Any
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.football_data import FootballDataClient
from app.config import get_settings

router = APIRouter(prefix="/standings", tags=["standings"])


@router.get("/{competition_id}", response_class=JSONResponse)
async def get_standings(competition_id: str) -> Any:
    client = FootballDataClient(api_key=get_settings().football_data_api_key)
    data = await client.get_standings(competition_id)
    return data
