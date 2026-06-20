from __future__ import annotations
import os
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.ml.features import build_features
from app.ml.model import WC2026Model

MODEL_PATHS = {
    "national":     os.getenv("ML_MODEL_NATIONAL", "ml_artifacts/lgbm_national.pkl"),
    "club_europe":  os.getenv("ML_MODEL_CLUB", "ml_artifacts/lgbm_club_europe.pkl"),
}

class Predictor:
    def __init__(self):
        self._models: dict[str, WC2026Model] = {}

    def _get_model(self, competition_type: str) -> WC2026Model | None:
        if competition_type not in self._models:
            path = MODEL_PATHS.get(competition_type, "")
            if os.path.exists(path):
                self._models[competition_type] = WC2026Model.load(path)
        return self._models.get(competition_type)

    def _run_model(
        self,
        competition_type: str,
        home_team: str,
        away_team: str,
        home_strength: float,
        away_strength: float,
        home_history: list[dict],
        away_history: list[dict],
        h2h: list[dict],
        stage: str,
        days_rest: int,
    ) -> dict:
        features = build_features(
            home_team=home_team, away_team=away_team,
            competition_type=competition_type,
            home_strength=home_strength, away_strength=away_strength,
            home_history=home_history, away_history=away_history,
            h2h=h2h, stage=stage, days_rest=days_rest,
        )
        model = self._get_model(competition_type)
        if model is None:
            probs = {"home_win": 0.40, "draw": 0.27, "away_win": 0.33, "confidence": "low"}
        else:
            probs = model.predict(features)

        h_goals = max(0, round(features["home_goals_scored_avg"] + features["home_advantage"] * 0.5))
        a_goals = max(0, round(features["away_goals_scored_avg"]))
        return {**probs, "predicted_score": f"{h_goals}-{a_goals}"}

    async def predict_match(self, match_id: int, db: AsyncSession) -> dict:
        from app.models.match import Match
        from app.models.competition import Competition
        from app.models.team_strength import TeamStrength

        match = await db.get(Match, match_id)
        comp = await db.get(Competition, match.competition_id)

        home_s = await db.scalar(
            select(TeamStrength.strength_value).where(
                TeamStrength.team_name == match.home_team,
                TeamStrength.competition_type == comp.competition_type,
            )
        ) or (1500.0 if comp.competition_type == "national" else 300.0)

        away_s = await db.scalar(
            select(TeamStrength.strength_value).where(
                TeamStrength.team_name == match.away_team,
                TeamStrength.competition_type == comp.competition_type,
            )
        ) or (1500.0 if comp.competition_type == "national" else 300.0)

        return self._run_model(
            competition_type=comp.competition_type,
            home_team=match.home_team, away_team=match.away_team,
            home_strength=home_s, away_strength=away_s,
            home_history=[], away_history=[], h2h=[],
            stage="GROUP", days_rest=4,
        )


@lru_cache(maxsize=1)
def get_predictor() -> Predictor:
    return Predictor()
