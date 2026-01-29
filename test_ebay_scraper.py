
import asyncio
import logging
import sys
import os

# Set root path
sys.path.append(os.getcwd())

from src.infrastructure.scrapers.ebay_scraper import EbayScraper

# Setup logging
logging.basicConfig(level=logging.INFO)

async def test_ebay():
    scraper = EbayScraper()
    print("🚀 Iniciando Test de EbayScraper (Extracción Masiva)...")
    
    # Test only 1 page for speed in verification
    offers = await scraper.search("masters of the universe origins")
    
    print(f"\n✅ Total capturado: {len(offers)} reliquias.")
    
    if offers:
        print("\n--- Muestra de resultados ---")
        for o in offers[:5]:
            print(f"- {o.product_name} | {o.price}€ | {o.url[:50]}...")
            if o.bids_count > 0:
                print(f"  [Subasta] Bids: {o.bids_count} | Expira: {o.expiry_at}")
    else:
        print("❌ No se capturaron ofertas. Revisa los logs.")

if __name__ == "__main__":
    asyncio.run(test_ebay())
