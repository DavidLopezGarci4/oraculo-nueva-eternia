import asyncio
from src.infrastructure.scrapers.action_toys_scraper import ActionToysScraper

async def test_actiontoys():
    scraper = ActionToysScraper()
    # Test query that should return results
    results = await scraper.search("Origins")
    
    print(f"\n--- Results ({len(results)}) ---")
    for r in results[:5]:
        print(f"[{r.shop_name}] {r.product_name} - {r.price}€")
        print(f"URL: {r.url}")
        print("---")

if __name__ == "__main__":
    asyncio.run(test_actiontoys())
