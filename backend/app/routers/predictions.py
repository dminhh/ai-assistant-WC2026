from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.match import Match
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionResponse
from app.ml.predictor import get_predictor

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/{match_id}", response_model=PredictionResponse)
async def get_prediction(match_id: int, db: AsyncSession = Depends(get_db)):
    CURRENT_MODEL = "v2-lgbm-poisson"
    existing = await db.scalar(
        select(Prediction)
        .where(Prediction.match_id == match_id, Prediction.model_version == CURRENT_MODEL)
        .order_by(Prediction.created_at.desc())
    )
    if existing:
        return existing

    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(404, "Match not found")

    result = await get_predictor().predict_match(match_id, db)

    pred = Prediction(
        match_id=match_id,
        home_win_prob=result["home_win"],
        draw_prob=result["draw"],
        away_win_prob=result["away_win"],
        predicted_score=result["predicted_score"],
        score_probs=result.get("score_probs"),
        confidence=result["confidence"],
        model_version="v2-lgbm-poisson",
        created_at=datetime.now(timezone.utc),
    )
    db.add(pred)
    await db.commit()
    await db.refresh(pred)
    return pred
