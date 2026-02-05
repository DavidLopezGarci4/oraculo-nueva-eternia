import asyncio
from src.infrastructure.scrapers.ebay_scraper import EbayScraper
from src.infrastructure.scrapers.ebay_es_advanced_scraper import EbayESAdvancedScraper

async def test_enhanced_scrapers():
    query = "masters of the universe origins he-man"
    
    scrapers = [
        EbayScraper(),
        EbayESAdvancedScraper()
    ]
    
    for scraper in scrapers:
        print(f"\n🚀 Testing Enhanced Scraper: {scraper.shop_name}")
        try:
            results = await scraper.search(query)
            print(f"✅ Total captured: {len(results)} items.")
            
            if results:
                print("\n--- Top 5 Results Sample ---")
                for i, offer in enumerate(results[:5]):
                    print(f"{i+1}. {offer.product_name}")
                    print(f"   Price: {offer.price}€ | Shipping: {offer.shipping_price}€ | TOTAL: {offer.total_price}€")
                    print(f"   URL: {offer.url[:60]}...")
            else:
                print("❌ No items captured.")
        except Exception as e:
            print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_scrapers())
