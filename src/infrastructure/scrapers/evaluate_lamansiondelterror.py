import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.infrastructure.scrapers.lamansiondelterror_scraper import LaMansionDelTerrorScraper

async def test_scraper():
    print("🚀 Probando Scraper de La Mansión del Terror...")
    scraper = LaMansionDelTerrorScraper()

    # Redirect logs to console
    scraper.log_callback = lambda msg: print(f"[LOG] {msg}")

    # Search for wwe masters tmnt of the universe origins
    results = await scraper.search("wwe masters tmnt of the universe origins")

    print("\n--- RESULTADOS ---")
    print(f"Total encontrados en stock: {len(results)}")

    for i, offer in enumerate(results[:10]):
        print(f"\n[{i+1}] {offer.product_name}")
        print(f"    Precio Actual: {offer.price} {offer.currency}")
        print(f"    Disponible: {offer.is_available}")
        print(f"    URL: {offer.url}")
        print(f"    Imagen: {offer.image_url}")

    if not results:
        print("⚠️ No se encontraron resultados. Verificar selectores o disponibilidad de la tienda.")
    else:
        print(f"\n✅ Test superado. {len(results)} ofertas en stock extraídas de lamansiondelterror.es")

if __name__ == "__main__":
    asyncio.run(test_scraper())
