import asyncio
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.infrastructure.scrapers.base import BaseScraper

class MockScraper(BaseScraper):
    async def search(self, query: str): return []

async def test_idealo():
    scraper = MockScraper("IdealoTest")
    url = "https://www.idealo.es/resultados.html?q=masters+of+the+universe+origins"
    html = await scraper._curl_get(url)
    if html:
        print(f"Success! HTML length: {len(html)}")
        with open("idealo_diagnostic.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("HTML saved to idealo_diagnostic.html")
    else:
        print("Failed to get HTML from Idealo")

if __name__ == "__main__":
    asyncio.run(test_idealo())
