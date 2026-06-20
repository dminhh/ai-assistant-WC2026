import re
import httpx
from bs4 import BeautifulSoup

FIFA_URL = "https://www.fifa.com/fifa-world-ranking/men"


class FifaRankingCrawler:
    async def fetch(self) -> list[dict]:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(follow_redirects=True) as client:
            r = await client.get(FIFA_URL, headers=headers)
            r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        # FIFA renders ranking in a table — parse rows
        for row in soup.select("table tr"):
            cells = row.find_all("td")
            if len(cells) >= 3:
                try:
                    team = cells[1].get_text(strip=True)
                    points_text = cells[2].get_text(strip=True).replace(",", ".")
                    points = float(re.sub(r"[^\d.]", "", points_text))
                    if team and points > 0:
                        results.append({"team": team, "points": points})
                except (ValueError, IndexError):
                    continue
        return results
