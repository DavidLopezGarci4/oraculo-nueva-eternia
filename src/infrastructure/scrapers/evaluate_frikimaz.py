import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.infrastructure.scrapers.frikimaz_scraper import FrikimazScraper

async def test_scraper():
    print("🚀 Probando Scraper de Frikimaz...")
    scraper = FrikimazScraper()

    # Redirect logs to console
    scraper.log_callback = lambda msg: print(f"[LOG] {msg}")

    results = await scraper.search("masters of the universe origins")

    print("\n--- RESULTADOS ---")
    print(f"Total encontrados: {len(results)}")

    for i, offer in enumerate(results[:5]):
        print(f"\n[{i+1}] {offer.product_name}")
        print(f"    Precio: {offer.price} {offer.currency}")
        print(f"    EAN: {offer.ean}")
        print(f"    Disponible: {offer.is_available}")
        print(f"    URL: {offer.url}")
        print(f"    Imagen: {offer.image_url}")

    if not results:
        print("⚠️ No se encontraron resultados. Verificar selectores o disponibilidad de la tienda.")
    else:
        print(f"\n✅ Test superado. {len(results)} ofertas extraídas de Frikimaz.es")

if __name__ == "__main__":
    asyncio.run(test_scraper())
