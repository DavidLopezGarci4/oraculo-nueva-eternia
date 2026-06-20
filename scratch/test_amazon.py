import asyncio
from dotenv import load_dotenv
import os
import sys

# Load env variables from .env file
load_dotenv()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.infrastructure.scrapers.amazon_scraper import AmazonScraper

async def main():
    print("SCRAPERAPI_KEY in env:", os.environ.get("SCRAPERAPI_KEY"))
    print("Running Amazon Scraper search...")
    
    scraper = AmazonScraper()
    scraper.log_callback = lambda msg: print(f"[LOG] {msg}")
    
    # We will search for a query
    results = await scraper.search("wwe masters tmnt of the universe origins")
    print(f"\nTotal offers found: {len(results)}")
    for idx, res in enumerate(results[:5]):
        print(f"[{idx+1}] {res.product_name} - {res.price} {res.currency} - URL: {res.url}")

if __name__ == "__main__":
    asyncio.run(main())
