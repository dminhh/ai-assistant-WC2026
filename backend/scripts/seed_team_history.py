"""
Seed 10 trận gần nhất (trước 2026-01-01) của mỗi đội từ CSV vào bảng team_history.
Run: cd backend && python scripts/seed_team_history.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import pandas as pd
from datetime import timezone
from collections import defaultdict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.config import get_settings
from app.models.team_history import TeamHistory

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "international_results.csv")
CUTOFF = "2026-01-01"
N = 10  # số trận gần nhất mỗi đội


async def main():
    print("Loading CSV...")
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df = df.dropna(subset=["home_score", "away_score"])
    df = df[df["date"] < CUTOFF].sort_values("date").reset_index(drop=True)
    print(f"Loaded {len(df)} matches before {CUTOFF}")

    # Gom lịch sử từng đội
    team_matches: dict = defaultdict(list)
    for _, row in df.iterrows():
        h, a = row["home_team"], row["away_team"]
        hs, as_ = int(row["home_score"]), int(row["away_score"])
        dt = row["date"].to_pydatetime().replace(tzinfo=timezone.utc)

        team_matches[h].append({
            "team_name": h, "opponent": a,
            "result": "W" if hs > as_ else ("D" if hs == as_ else "L"),
            "goals_scored": hs, "goals_conceded": as_,
            "match_date": dt,
        })
        team_matches[a].append({
            "team_name": a, "opponent": h,
            "result": "W" if as_ > hs else ("D" if as_ == hs else "L"),
            "goals_scored": as_, "goals_conceded": hs,
            "match_date": dt,
        })

    # Lấy 10 trận gần nhất mỗi đội
    rows = []
    for team, matches in team_matches.items():
        rows.extend(matches[-N:])

    print(f"Seeding {len(rows)} rows for {len(team_matches)} teams...")

    engine = create_async_engine(get_settings().database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Tạo bảng nếu chưa có
    from app.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        async with session.begin():
            stmt = pg_insert(TeamHistory).values(rows)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_team_history",
                set_={
                    "result": stmt.excluded.result,
                    "goals_scored": stmt.excluded.goals_scored,
                    "goals_conceded": stmt.excluded.goals_conceded,
                },
            )
            await session.execute(stmt)

    print("Done!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
