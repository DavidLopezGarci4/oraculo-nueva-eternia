import asyncio
import sys
from pathlib import Path
import logging

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.infrastructure.scrapers.vinted_scraper import VintedScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def run():
    v = VintedScraper()
    v.max_pages = 1
    query = "masters of the universe origins"
    print(f"\n🔍 [VINTED TEST] Iniciando prueba con query='{query}'...")
    items = await v.search(query)
    print(f"\n✅ [VINTED TEST] Completado. Encontrados {len(items)} items.")
    
    if items:
        print("\n📦 Muestra de los primeros 5 items:")
        for idx, item in enumerate(items[:5], 1):
            print(f"  {idx}. [{item.price:.2f}€] {item.product_name}")
            print(f"     URL: {item.url}")
            print(f"     Img: {item.image_url}")
    else:
        print("⚠️ No se encontraron items.")

if __name__ == "__main__":
    asyncio.run(run())
