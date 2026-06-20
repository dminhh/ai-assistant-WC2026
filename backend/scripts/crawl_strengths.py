"""
Crawl FIFA Points và Transfermarkt Squad Value, lưu vào DB.
Chạy thủ công hàng tháng:
  cd backend && python scripts/crawl_strengths.py
"""
import sys
import os

# Must set/load env vars BEFORE importing app modules, because app/database.py
# calls get_settings() at import time.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    # python-dotenv not installed — rely on env vars already being set
    pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.team_strength import TeamStrength
from app.crawlers.fifa_ranking import FifaRankingCrawler
from app.crawlers.transfermarkt import TransfermarktCrawler


async def upsert_strength(db, team_name: str, competition_type: str, value: float):
    existing = await db.scalar(
        select(TeamStrength).where(
            TeamStrength.team_name == team_name,
            TeamStrength.competition_type == competition_type,
        )
    )
    if existing:
        existing.strength_value = value
        existing.updated_at = datetime.now(timezone.utc)
    else:
        db.add(TeamStrength(
            team_name=team_name,
            competition_type=competition_type,
            strength_value=value,
            updated_at=datetime.now(timezone.utc),
        ))


async def main():
    async with AsyncSessionLocal() as db:
        # ĐTQG: FIFA Points
        print("Crawling FIFA rankings...")
        fifa_data = await FifaRankingCrawler().fetch()
        for item in fifa_data:
            await upsert_strength(db, item["team"], "national", item["points"])
        print(f"  → {len(fifa_data)} national teams updated")

        # Club: Transfermarkt Squad Value
        print("Crawling Transfermarkt squad values...")
        tm = TransfermarktCrawler()
        club_data = await tm.fetch_all_leagues()
        for item in club_data:
            await upsert_strength(db, item["team"], "club_europe", item["value_m"])
        print(f"  → {len(club_data)} clubs updated")

        await db.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
