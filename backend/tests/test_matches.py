# tests/test_matches.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_db
from app.models.competition import Competition
from app.models.match import Match
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_get_today_matches(db_session):
    # Override the get_db dependency to use test session
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        comp = Competition(name="WC2026", api_competition_id="2000", is_active=True, season="2026")
        db_session.add(comp)
        await db_session.commit()
        await db_session.refresh(comp)

        match = Match(
            competition_id=comp.id,
            home_team="Brazil", away_team="France",
            kickoff_time=datetime.now(timezone.utc),
            status="upcoming", api_match_id="test_001"
        )
        db_session.add(match)
        await db_session.commit()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.get("/matches/today")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert data[0]["home_team"] == "Brazil"
    finally:
        app.dependency_overrides.clear()
