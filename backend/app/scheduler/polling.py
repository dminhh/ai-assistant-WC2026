# app/scheduler/polling.py
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.services.football_data import FootballDataClient
from app.services.sync import sync_matches
from app.models.competition import Competition
from app.models.match import Match
from app.config import get_settings

scheduler = AsyncIOScheduler()

async def _get_active_competitions(db):
    result = await db.execute(select(Competition).where(Competition.is_active == True))
    return result.scalars().all()

async def _has_live_match(db) -> bool:
    result = await db.execute(select(Match).where(Match.status == "live"))
    return result.first() is not None

async def _has_upcoming_soon(db) -> bool:
    """Có trận nào bắt đầu trong 2 tiếng tới không."""
    now = datetime.now(timezone.utc)
    soon = now + timedelta(hours=2)
    result = await db.execute(
        select(Match).where(Match.status == "upcoming", Match.kickoff_time <= soon)
    )
    return result.first() is not None

async def poll_job():
    """Job chính — chạy mỗi phút, tự quyết định có fetch không."""
    settings = get_settings()
    client = FootballDataClient(api_key=settings.football_data_api_key)
    async with AsyncSessionLocal() as db:
        is_live = await _has_live_match(db)
        is_soon = await _has_upcoming_soon(db)

        # Live: fetch mỗi lần job chạy (mỗi 3 phút theo schedule bên dưới)
        # Sắp đá: fetch mỗi 30 phút (job riêng)
        # Không có gì: không fetch
        if is_live or is_soon:
            competitions = await _get_active_competitions(db)
            for comp in competitions:
                await sync_matches(db, client, comp.api_competition_id, comp.id)

async def poll_slow_job():
    """Fetch mỗi 6 tiếng — fixtures và standings khi không có trận."""
    settings = get_settings()
    client = FootballDataClient(api_key=settings.football_data_api_key)
    async with AsyncSessionLocal() as db:
        is_live = await _has_live_match(db)
        is_soon = await _has_upcoming_soon(db)
        if not is_live and not is_soon:
            competitions = await _get_active_competitions(db)
            for comp in competitions:
                await sync_matches(db, client, comp.api_competition_id, comp.id)

def start_scheduler():
    # Poll nhanh (mỗi 3 phút) — chỉ chạy khi có trận live/sắp đá
    scheduler.add_job(poll_job, "interval", minutes=3, id="poll_fast")
    # Poll chậm (mỗi 6 tiếng) — khi không có trận
    scheduler.add_job(poll_slow_job, "interval", hours=6, id="poll_slow")
    scheduler.start()
