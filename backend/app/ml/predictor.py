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
        is_neutral: bool = False,
        tournament: str = "",
    ) -> dict:
        from app.ml.poisson import estimate_lambdas, predict_score

        features = build_features(
            home_team=home_team, away_team=away_team,
            competition_type=competition_type,
            home_strength=home_strength, away_strength=away_strength,
            home_history=home_history, away_history=away_history,
            h2h=h2h, stage=stage, days_rest=days_rest,
            is_neutral=is_neutral, tournament=tournament,
        )
        model = self._get_model(competition_type)
        if model is None:
            lgbm_confidence = "low"
        else:
            lgbm_result = model.predict(features)
            lgbm_confidence = lgbm_result["confidence"]

        # Poisson cho cả tỷ lệ thắng/hòa/thua và tỷ số
        lambda_home, lambda_away = estimate_lambdas(features)
        poisson = predict_score(lambda_home, lambda_away)

        return {
            "home_win": poisson["home_win_prob"],
            "draw": poisson["draw_prob"],
            "away_win": poisson["away_win_prob"],
            "confidence": lgbm_confidence,
            "predicted_score": poisson["predicted_score"],
            "score_probs": poisson["score_probs"],
        }

    async def predict_match(self, match_id: int, db: AsyncSession) -> dict:
        from app.models.match import Match
        from app.models.competition import Competition
        from app.models.team_strength import TeamStrength

        match = await db.get(Match, match_id)
        if match is None:
            raise ValueError(f"Match {match_id} not found")

        comp = await db.get(Competition, match.competition_id)
        if comp is None:
            raise ValueError(f"Competition {match.competition_id} not found")

        _default_strength = 1500.0 if comp.competition_type == "national" else 300.0

        home_s = await db.scalar(
            select(TeamStrength.strength_value).where(
                TeamStrength.team_name == match.home_team,
                TeamStrength.competition_type == comp.competition_type,
            )
        ) or _default_strength

        away_s = await db.scalar(
            select(TeamStrength.strength_value).where(
                TeamStrength.team_name == match.away_team,
                TeamStrength.competition_type == comp.competition_type,
            )
        ) or _default_strength

        # Lấy lịch sử 10 trận gần nhất của mỗi đội từ DB (finished matches)
        home_history = await self._fetch_team_history(db, match.home_team, match.kickoff_time)
        away_history = await self._fetch_team_history(db, match.away_team, match.kickoff_time)
        h2h = await self._fetch_h2h(db, match.home_team, match.away_team, match.kickoff_time)

        return self._run_model(
            competition_type=comp.competition_type,
            home_team=match.home_team, away_team=match.away_team,
            home_strength=home_s, away_strength=away_s,
            home_history=home_history, away_history=away_history,
            h2h=h2h,
            stage="GROUP", days_rest=4,
            is_neutral=True,
            tournament="FIFA World Cup",
        )

    async def _fetch_team_history(self, db: AsyncSession, team: str, before) -> list[dict]:
        from app.models.match import Match
        from app.models.team_history import TeamHistory
        result = await db.execute(
            select(Match)
            .where(
                Match.status == "finished",
                Match.kickoff_time < before,
                (Match.home_team == team) | (Match.away_team == team),
            )
            .order_by(Match.kickoff_time.desc())
            .limit(10)
        )
        matches = result.scalars().all()
        history = []
        for m in matches:
            if m.home_score is None or m.away_score is None:
                continue
            if m.home_team == team:
                gs, gc = m.home_score, m.away_score
            else:
                gs, gc = m.away_score, m.home_score
            result_str = "W" if gs > gc else ("D" if gs == gc else "L")
            history.append({"result": result_str, "goals_scored": gs, "goals_conceded": gc})

        # Nếu ít hơn 5 trận WC, fallback sang lịch sử từ CSV
        if len(history) < 5:
            hist_result = await db.execute(
                select(TeamHistory)
                .where(TeamHistory.team_name == team)
                .order_by(TeamHistory.match_date.desc())
                .limit(10 - len(history))
            )
            for h in hist_result.scalars().all():
                history.append({
                    "result": h.result,
                    "goals_scored": h.goals_scored,
                    "goals_conceded": h.goals_conceded,
                })

        return history

    async def _fetch_h2h(self, db: AsyncSession, home: str, away: str, before) -> list[dict]:
        from app.models.match import Match
        result = await db.execute(
            select(Match)
            .where(
                Match.status == "finished",
                Match.kickoff_time < before,
                ((Match.home_team == home) & (Match.away_team == away)) |
                ((Match.home_team == away) & (Match.away_team == home)),
            )
            .order_by(Match.kickoff_time.desc())
            .limit(5)
        )
        matches = result.scalars().all()
        h2h = []
        for m in matches:
            if m.home_score is None or m.away_score is None:
                continue
            if m.home_team == home:
                h2h.append({"home_goals": m.home_score, "away_goals": m.away_score})
            else:
                h2h.append({"home_goals": m.away_score, "away_goals": m.home_score})
        return h2h


@lru_cache(maxsize=1)
def get_predictor() -> Predictor:
    return Predictor()
