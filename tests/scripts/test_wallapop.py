import asyncio
import logging
from src.infrastructure.scrapers.wallapop_scraper import WallapopScraper

logging.basicConfig(level=logging.INFO)

async def run():
    w = WallapopScraper()
    items = await w.search("masters of the universe origins")
    print(f"WALLAPOP TEST: Found {len(items)} items")

asyncio.run(run())
