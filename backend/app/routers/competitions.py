# app/routers/competitions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.competition import Competition
from app.schemas.competition import CompetitionResponse

router = APIRouter(prefix="/competitions", tags=["competitions"])


@router.get("", response_model=list[CompetitionResponse])
async def list_competitions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competition))
    return result.scalars().all()


@router.patch("/{competition_id}/toggle", response_model=CompetitionResponse)
async def toggle_competition(competition_id: int, db: AsyncSession = Depends(get_db)):
    comp = await db.get(Competition, competition_id)
    if not comp:
        raise HTTPException(404, "Competition not found")
    comp.is_active = not comp.is_active
    await db.commit()
    await db.refresh(comp)
    return comp
