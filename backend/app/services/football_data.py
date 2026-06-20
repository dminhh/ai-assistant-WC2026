import httpx

BASE_URL = "https://api.football-data.org/v4"


class FootballDataClient:
    def __init__(self, api_key: str):
        self._headers = {"X-Auth-Token": api_key}
        self._client = httpx.AsyncClient(headers=self._headers, timeout=30.0)

    async def get_competitions(self) -> list[dict]:
        r = await self._client.get(f"{BASE_URL}/competitions")
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
        r = await self._client.get(
            f"{BASE_URL}/competitions/{competition_id}/matches",
            params=params,
        )
        r.raise_for_status()
        return r.json()["matches"]

    async def get_standings(self, competition_id: str) -> list[dict]:
        r = await self._client.get(
            f"{BASE_URL}/competitions/{competition_id}/standings",
        )
        r.raise_for_status()
        return r.json()["standings"]

    async def aclose(self):
        await self._client.aclose()
