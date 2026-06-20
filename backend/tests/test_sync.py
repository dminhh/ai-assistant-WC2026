import pytest
from unittest.mock import AsyncMock
from app.services.sync import sync_matches
from app.models.competition import Competition


@pytest.mark.asyncio
async def test_sync_matches_creates_new(db_session):
    # create competition first
    comp = Competition(
        name="WC2026", api_competition_id="2000",
        is_active=True, season="2026"
    )
    db_session.add(comp)
    await db_session.commit()
    await db_session.refresh(comp)

    mock_client = AsyncMock()
    mock_client.get_matches.return_value = [{
        "id": 999,
        "homeTeam": {"name": "Brazil"},
        "awayTeam": {"name": "France"},
        "utcDate": "2026-06-20T17:00:00Z",
        "status": "SCHEDULED",
        "score": {"fullTime": {"home": None, "away": None}},
    }]

    count = await sync_matches(db_session, mock_client, competition_id="2000", db_competition_id=comp.id)
    assert count == 1


@pytest.mark.asyncio
async def test_sync_matches_upserts_existing(db_session):
    comp = Competition(
        name="WC2026", api_competition_id="2000",
        is_active=True, season="2026"
    )
    db_session.add(comp)
    await db_session.commit()

    mock_client = AsyncMock()
    match_data = [{
        "id": 999,
        "homeTeam": {"name": "Brazil"},
        "awayTeam": {"name": "France"},
        "utcDate": "2026-06-20T17:00:00Z",
        "status": "FINISHED",
        "score": {"fullTime": {"home": 2, "away": 1}},
    }]
    mock_client.get_matches.return_value = match_data

    # sync first time
    await sync_matches(db_session, mock_client, "2000", comp.id)
    # sync second time — must upsert, not duplicate
    count = await sync_matches(db_session, mock_client, "2000", comp.id)
    assert count == 1
