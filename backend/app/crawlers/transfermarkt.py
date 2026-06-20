import re
import httpx
from bs4 import BeautifulSoup


class TransfermarktCrawler:
    # URLs for top 5 leagues
    LEAGUE_URLS = {
        "premier_league": "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1",
        "la_liga":        "https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1",
        "serie_a":        "https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1",
        "bundesliga":     "https://www.transfermarkt.com/1-bundesliga/startseite/wettbewerb/L1",
        "ligue_1":        "https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1",
    }

    async def fetch(self, league_url: str) -> list[dict]:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
        }
        async with httpx.AsyncClient(follow_redirects=True) as client:
            r = await client.get(league_url, headers=headers)
            r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for row in soup.select("table.items tr"):
            name_cell = row.select_one("td.hauptlink a")
            value_cell = row.select_one("td.rechts.hauptlink")
            if name_cell and value_cell:
                team = name_cell.get_text(strip=True)
                raw = value_cell.get_text(strip=True)  # e.g. "€850.00m"
                match = re.search(r"[\d.]+", raw)
                if match and team:
                    value_m = float(match.group())
                    # Transfermarkt sometimes uses bn (billion) → convert
                    if "bn" in raw.lower():
                        value_m *= 1000
                    results.append({"team": team, "value_m": value_m})
        return results

    async def fetch_all_leagues(self) -> list[dict]:
        results = []
        for league_url in self.LEAGUE_URLS.values():
            try:
                clubs = await self.fetch(league_url)
                results.extend(clubs)
            except Exception:
                continue
        return results
