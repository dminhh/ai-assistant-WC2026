from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.models.match import Match
from app.models.competition import Competition
from app.models.team_history import TeamHistory

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
    rows = []
    for m in raw_matches:
        home_team = m["homeTeam"].get("name")
        away_team = m["awayTeam"].get("name")
        # Bỏ qua trận chưa xác định đội (vòng knock-out TBD)
        if not home_team or not away_team:
            continue

        score = m.get("score", {}).get("fullTime", {})
        api_status = m["status"]
        minute = None
        if api_status in ("IN_PLAY", "PAUSED"):
            minute = m.get("minute")
        rows.append({
            "api_match_id": str(m["id"]),
            "competition_id": db_competition_id,
            "home_team": home_team,
            "away_team": away_team,
            "kickoff_time": datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00")),
            "status": STATUS_MAP.get(api_status, "upcoming"),
            "home_score": score.get("home"),
            "away_score": score.get("away"),
            "minute": minute,
        })

    if not rows:
        return 0

    stmt = pg_insert(Match).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["api_match_id"],
        set_={
            "status": stmt.excluded.status,
            "home_score": stmt.excluded.home_score,
            "away_score": stmt.excluded.away_score,
            "home_team": stmt.excluded.home_team,
            "away_team": stmt.excluded.away_team,
            "minute": stmt.excluded.minute,
        },
    )
    await db.execute(stmt)
    await db.commit()

    # Cập nhật team_history cho các trận đã kết thúc
    finished = [r for r in rows if r["status"] == "finished"
                and r["home_score"] is not None and r["away_score"] is not None]
    if finished:
        history_rows = []
        for r in finished:
            hs, as_ = r["home_score"], r["away_score"]
            dt = r["kickoff_time"] if r["kickoff_time"].tzinfo else r["kickoff_time"].replace(tzinfo=timezone.utc)
            history_rows.append({
                "team_name": r["home_team"], "opponent": r["away_team"],
                "result": "W" if hs > as_ else ("D" if hs == as_ else "L"),
                "goals_scored": hs, "goals_conceded": as_, "match_date": dt,
            })
            history_rows.append({
                "team_name": r["away_team"], "opponent": r["home_team"],
                "result": "W" if as_ > hs else ("D" if as_ == hs else "L"),
                "goals_scored": as_, "goals_conceded": hs, "match_date": dt,
            })
        hist_stmt = pg_insert(TeamHistory).values(history_rows)
        hist_stmt = hist_stmt.on_conflict_do_update(
            constraint="uq_team_history",
            set_={
                "result": hist_stmt.excluded.result,
                "goals_scored": hist_stmt.excluded.goals_scored,
                "goals_conceded": hist_stmt.excluded.goals_conceded,
            },
        )
        await db.execute(hist_stmt)
        await db.commit()

    return len(rows)
