import asyncio
import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())

# Load environment
load_dotenv(override=True)

# Map of scraper names to their classes
def get_scraper_class(name: str):
    from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper
    from src.infrastructure.scrapers.wallapop_scraper import WallapopScraper
    from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
    from src.infrastructure.scrapers.ebay_scraper import EbayScraper
    from src.infrastructure.scrapers.vinted_scraper import VintedScraper
    from src.infrastructure.scrapers.bbts_scraper import BigBadToyStoreScraper
    
    scrapers = {
        "SmythsToys": SmythsToysScraper,
        "Wallapop": WallapopScraper,
        "Amazon": AmazonScraper,
        "Ebay": EbayScraper,
        "Vinted": VintedScraper,
        "BBTS": BigBadToyStoreScraper
    }
    return scrapers.get(name)

async def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/run_single_incursion.py <ScraperName> [query]")
        return
        
    scraper_name = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) > 2 else "auto"
    
    scraper_cls = get_scraper_class(scraper_name)
    if not scraper_cls:
        print(f"Error: Scraper '{scraper_name}' no soportado o no registrado en el script.")
        print("Soportados: SmythsToys, Wallapop, Amazon, Ebay, Vinted, BBTS")
        return
        
    print(f"🚀 Iniciando incursion local para {scraper_name} (query='{query}')...")
    scraper = scraper_cls()
    
    try:
        offers = await scraper.search(query)
        print(f"\n✅ Incursion completada para {scraper_name}!")
        print(f"Reliquias encontradas: {len(offers)}")
        print("------------------------------------------")
        for i, offer in enumerate(offers[:15]):
            print(f"{i+1:02d}. {offer.product_name}")
            print(f"    Precio: {offer.price} {offer.currency} | Disponible: {offer.is_available}")
            print(f"    URL: {offer.url}")
        if len(offers) > 15:
            print(f"... y {len(offers) - 15} ofertas más.")
    except Exception as e:
        print(f"❌ Error durante la ejecucion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
