from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.match import Match
from app.models.competition import Competition

STATUS_MAP = {
    "SCHEDULED": "upcoming",
    "TIMED": "upcoming",
    "IN_PLAY": "live",
    "PAUSED": "live",
    "FINISHED": "finished",
    "CANCELLED": "finished",
}


async def sync_competitions(db: AsyncSession, client) -> int:
    competitions = await client.get_competitions()
    count = 0
    for c in competitions:
        existing = await db.scalar(
            select(Competition).where(Competition.api_competition_id == str(c["id"]))
        )
        if not existing:
            db.add(Competition(
                name=c["name"],
                api_competition_id=str(c["id"]),
                is_active=False,
                country=c.get("area", {}).get("name"),
            ))
            count += 1
    await db.commit()
    return count


async def sync_matches(
    db: AsyncSession,
    client,
    competition_id: str,
    db_competition_id: int,
) -> int:
    raw_matches = await client.get_matches(competition_id=competition_id)
    count = 0
    for m in raw_matches:
        api_id = str(m["id"])
        existing = await db.scalar(select(Match).where(Match.api_match_id == api_id))
        score = m.get("score", {}).get("fullTime", {})
        status = STATUS_MAP.get(m["status"], "upcoming")

        home_team = m["homeTeam"].get("name")
        away_team = m["awayTeam"].get("name")

        if existing:
            existing.status = status
            existing.home_score = score.get("home")
            existing.away_score = score.get("away")
            # Cập nhật tên đội nếu trước đó chưa có (TBD → tên thật)
            if home_team:
                existing.home_team = home_team
            if away_team:
                existing.away_team = away_team
        else:
            # Bỏ qua trận chưa xác định đội (vòng knock-out TBD)
            if not home_team or not away_team:
                continue
            db.add(Match(
                competition_id=db_competition_id,
                home_team=home_team,
                away_team=away_team,
                kickoff_time=datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00")),
                status=status,
                home_score=score.get("home"),
                away_score=score.get("away"),
                api_match_id=api_id,
            ))
        count += 1
    await db.commit()
    return count
