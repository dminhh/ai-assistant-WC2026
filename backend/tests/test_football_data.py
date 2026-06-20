import pytest
import httpx
import respx
from app.services.football_data import FootballDataClient


@respx.mock
@pytest.mark.asyncio
async def test_get_competitions():
    respx.get("https://api.football-data.org/v4/competitions").mock(
        return_value=httpx.Response(200, json={
            "competitions": [
                {"id": 2000, "name": "FIFA World Cup", "area": {"name": "World"}}
            ]
        })
    )
    client = FootballDataClient(api_key="test_key")
    result = await client.get_competitions()
    assert len(result) == 1
    assert result[0]["name"] == "FIFA World Cup"


@respx.mock
@pytest.mark.asyncio
async def test_get_matches_today():
    respx.get("https://api.football-data.org/v4/competitions/2000/matches").mock(
        return_value=httpx.Response(200, json={
            "matches": [
                {
                    "id": 123,
                    "homeTeam": {"name": "Brazil"},
                    "awayTeam": {"name": "France"},
                    "utcDate": "2026-06-20T17:00:00Z",
                    "status": "SCHEDULED",
                    "score": {"fullTime": {"home": None, "away": None}},
                }
            ]
        })
    )
    client = FootballDataClient(api_key="test_key")
    result = await client.get_matches(competition_id="2000")
    assert result[0]["homeTeam"]["name"] == "Brazil"


@respx.mock
@pytest.mark.asyncio
async def test_get_matches_with_status():
    respx.get("https://api.football-data.org/v4/competitions/2000/matches").mock(
        return_value=httpx.Response(200, json={
            "matches": [
                {
                    "id": 456,
                    "homeTeam": {"name": "Argentina"},
                    "awayTeam": {"name": "Germany"},
                    "utcDate": "2026-06-20T20:00:00Z",
                    "status": "FINISHED",
                    "score": {"fullTime": {"home": 2, "away": 1}},
                }
            ]
        })
    )
    client = FootballDataClient(api_key="test_key")
    result = await client.get_matches(competition_id="2000", status="FINISHED")
    assert result[0]["status"] == "FINISHED"
    assert result[0]["score"]["fullTime"]["home"] == 2


@respx.mock
@pytest.mark.asyncio
async def test_get_standings():
    respx.get("https://api.football-data.org/v4/competitions/2000/standings").mock(
        return_value=httpx.Response(200, json={
            "standings": [
                {
                    "stage": "GROUP_STAGE",
                    "type": "TOTAL",
                    "group": "GROUP_A",
                    "table": [
                        {"position": 1, "team": {"name": "Brazil"}, "points": 9}
                    ],
                }
            ]
        })
    )
    client = FootballDataClient(api_key="test_key")
    result = await client.get_standings(competition_id="2000")
    assert len(result) == 1
    assert result[0]["group"] == "GROUP_A"
    assert result[0]["table"][0]["team"]["name"] == "Brazil"
