import asyncio
from src.infrastructure.scrapers.vinted_scraper import VintedScraper
import logging

logging.basicConfig(level=logging.INFO)

async def run():
    v = VintedScraper()
    v.max_pages = 1
    items = await v.search("masters of the universe origins")
    print(f"VINTED TEST: Found {len(items)} items")

asyncio.run(run())
