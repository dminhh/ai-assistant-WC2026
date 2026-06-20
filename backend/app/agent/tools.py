import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.match import Match
from app.models.competition import Competition
from app.ml.predictor import get_predictor


async def get_today_fixtures(db: AsyncSession) -> str:
    """Get list of today's matches."""
    today = datetime.now(timezone.utc).date()
    start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    result = await db.execute(
        select(Match).where(
            Match.kickoff_time >= start,
            Match.kickoff_time < end,
        )
    )
    matches = result.scalars().all()
    return json.dumps([
        {
            "id": m.id,
            "home_team": m.home_team,
            "away_team": m.away_team,
            "kickoff_time": m.kickoff_time.isoformat(),
            "status": m.status,
        }
        for m in matches
    ], ensure_ascii=False)


async def get_live_scores(db: AsyncSession) -> str:
    """Get scores of live matches."""
    result = await db.execute(select(Match).where(Match.status == "live"))
    matches = result.scalars().all()
    return json.dumps([
        {
            "home_team": m.home_team,
            "away_team": m.away_team,
            "home_score": m.home_score,
            "away_score": m.away_score,
        }
        for m in matches
    ], ensure_ascii=False)


async def get_standings(competition_name: str, db: AsyncSession) -> str:
    """Get standings for a competition."""
    comp = await db.scalar(
        select(Competition).where(
            Competition.name.ilike(f"%{competition_name}%"),
            Competition.is_active == True,
        )
    )
    if not comp:
        return json.dumps({"error": f"Competition '{competition_name}' not found"})
    from app.services.football_data import FootballDataClient
    from app.config import get_settings
    client = FootballDataClient(api_key=get_settings().football_data_api_key)
    try:
        standings = await client.get_standings(comp.api_competition_id)
        return json.dumps(standings, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def get_team_stats(team_name: str, db: AsyncSession) -> str:
    """Get stats from last 5 matches for a team."""
    result = await db.execute(
        select(Match).where(
            (Match.home_team.ilike(f"%{team_name}%")) |
            (Match.away_team.ilike(f"%{team_name}%")),
            Match.status == "finished",
        ).order_by(Match.kickoff_time.desc()).limit(5)
    )
    matches = result.scalars().all()
    stats = []
    for m in matches:
        is_home = team_name.lower() in m.home_team.lower()
        goals_for = m.home_score if is_home else m.away_score
        goals_against = m.away_score if is_home else m.home_score
        opponent = m.away_team if is_home else m.home_team
        result_str = "W" if goals_for > goals_against else ("D" if goals_for == goals_against else "L")
        stats.append({
            "opponent": opponent,
            "score": f"{goals_for}-{goals_against}",
            "result": result_str,
            "date": m.kickoff_time.strftime("%Y-%m-%d"),
        })
    return json.dumps({"team": team_name, "last_5": stats}, ensure_ascii=False)


async def get_prediction(home_team: str, away_team: str, db: AsyncSession) -> str:
    """Predict match outcome probabilities between two teams."""
    match = await db.scalar(
        select(Match).where(
            Match.home_team.ilike(f"%{home_team}%"),
            Match.away_team.ilike(f"%{away_team}%"),
            Match.status == "upcoming",
        ).order_by(Match.kickoff_time.asc())
    )
    if match:
        result = await get_predictor().predict_match(match.id, db)
    else:
        result = {
            "home_win": 0.40,
            "draw": 0.27,
            "away_win": 0.33,
            "predicted_score": "N/A",
            "confidence": "low",
            "note": f"No upcoming match found for {home_team} vs {away_team}",
        }
    return json.dumps(result, ensure_ascii=False)


async def get_h2h(team_a: str, team_b: str, db: AsyncSession) -> str:
    """Get head-to-head history between two teams (last 10 matches)."""
    result = await db.execute(
        select(Match).where(
            (
                (Match.home_team.ilike(f"%{team_a}%")) &
                (Match.away_team.ilike(f"%{team_b}%"))
            ) | (
                (Match.home_team.ilike(f"%{team_b}%")) &
                (Match.away_team.ilike(f"%{team_a}%"))
            ),
            Match.status == "finished",
        ).order_by(Match.kickoff_time.desc()).limit(10)
    )
    matches = result.scalars().all()
    return json.dumps([
        {
            "home_team": m.home_team,
            "away_team": m.away_team,
            "score": f"{m.home_score}-{m.away_score}",
            "date": m.kickoff_time.strftime("%Y-%m-%d"),
        }
        for m in matches
    ], ensure_ascii=False)
