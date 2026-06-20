# app/routers/admin.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.competition import Competition
from app.services.football_data import FootballDataClient
from app.services.sync import sync_matches
from app.config import get_settings

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/sync")
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    """Trigger sync matches cho tất cả active competitions ngay lập tức."""
    settings = get_settings()
    client = FootballDataClient(api_key=settings.football_data_api_key)
    synced = []
    try:
        result = await db.execute(select(Competition).where(Competition.is_active == True))
        competitions = result.scalars().all()
        for comp in competitions:
            await sync_matches(db, client, comp.api_competition_id, comp.id)
            synced.append(comp.name)
    finally:
        await client.aclose()
    return {"synced": synced}
