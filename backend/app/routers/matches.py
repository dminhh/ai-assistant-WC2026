# app/routers/matches.py
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.match import Match
from app.schemas.match import MatchResponse

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/today", response_model=list[MatchResponse])
async def get_today_matches(db: AsyncSession = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
    end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
    result = await db.execute(
        select(Match).where(
            Match.kickoff_time >= start,
            Match.kickoff_time < end,
        )
    )
    return result.scalars().all()


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(404, "Match not found")
    return match
