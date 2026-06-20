import httpx

BASE_URL = "https://api.football-data.org/v4"


class FootballDataClient:
    def __init__(self, api_key: str):
        self._headers = {"X-Auth-Token": api_key}

    async def get_competitions(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{BASE_URL}/competitions", headers=self._headers)
            r.raise_for_status()
            return r.json()["competitions"]

    async def get_matches(
        self,
        competition_id: str,
        status: str | None = None,
    ) -> list[dict]:
        params = {}
        if status:
            params["status"] = status
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{BASE_URL}/competitions/{competition_id}/matches",
                headers=self._headers,
                params=params,
            )
            r.raise_for_status()
            return r.json()["matches"]

    async def get_standings(self, competition_id: str) -> list[dict]:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{BASE_URL}/competitions/{competition_id}/standings",
                headers=self._headers,
            )
            r.raise_for_status()
            return r.json()["standings"]
