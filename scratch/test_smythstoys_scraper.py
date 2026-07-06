import asyncio
from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper

async def test_run():
    print("Initializing SmythsToysScraper...")
    scraper = SmythsToysScraper()
    
    print("Running scraper search (this will try to fetch the MOTU category page)...")
    try:
        offers = await scraper.search("auto")
        print(f"Scraper Run Finished.")
        print(f"  Blocked: {scraper.blocked}")
        print(f"  Errors: {scraper.errors}")
        print(f"  Items Scraped: {scraper.items_scraped}")
        print(f"  Offers Found: {len(offers)}")
        for idx, o in enumerate(offers[:5]):
            print(f"    {idx}: '{o.product_name}' - {o.price} {o.currency} (Available: {o.is_available})")
            print(f"       URL: {o.url}")
            print(f"       Img: {o.image_url}")
    except Exception as e:
        print(f"Critical error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_run())
