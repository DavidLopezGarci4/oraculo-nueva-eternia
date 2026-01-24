import asyncio
from src.infrastructure.scrapers.action_toys_scraper import ActionToysScraper
from src.core.logger import setup_logging

async def main():
    setup_logging()
    scraper = ActionToysScraper()
    print("Running ActionToysScraper directly...")
    items = await scraper.search("auto")
    print(f"Found {len(items)} items.")
    for i in items[:3]:
        print(f"- {i.product_name} ({i.price} EUR)")

if __name__ == "__main__":
    asyncio.run(main())
