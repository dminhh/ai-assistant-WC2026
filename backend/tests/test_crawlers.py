import pytest
import httpx
import respx
from app.crawlers.fifa_ranking import FifaRankingCrawler
from app.crawlers.transfermarkt import TransfermarktCrawler


@respx.mock
@pytest.mark.asyncio
async def test_fifa_crawler_returns_teams():
    html = """
    <table class="fifa-table">
      <tr><td>1</td><td>Brazil</td><td>1823.45</td></tr>
      <tr><td>2</td><td>France</td><td>1756.20</td></tr>
    </table>
    """
    respx.get("https://www.fifa.com/fifa-world-ranking/men").mock(
        return_value=httpx.Response(200, text=html)
    )
    crawler = FifaRankingCrawler()
    results = await crawler.fetch()
    assert len(results) >= 1
    assert all("team" in r and "points" in r for r in results)


@respx.mock
@pytest.mark.asyncio
async def test_transfermarkt_crawler_returns_clubs():
    html = """
    <table class="items">
      <tr><td class="hauptlink"><a>Manchester City</a></td>
          <td class="rechts hauptlink">€850.00m</td></tr>
      <tr><td class="hauptlink"><a>Arsenal</a></td>
          <td class="rechts hauptlink">€620.00m</td></tr>
    </table>
    """
    respx.get("https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1").mock(
        return_value=httpx.Response(200, text=html)
    )
    crawler = TransfermarktCrawler()
    results = await crawler.fetch("https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1")
    assert len(results) >= 1
    assert all("team" in r and "value_m" in r for r in results)
    assert results[0]["value_m"] == 850.0
