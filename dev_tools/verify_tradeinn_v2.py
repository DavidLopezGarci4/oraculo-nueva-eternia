import asyncio
import sys
import os
from loguru import logger

# Añadir el raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.scrapers.tradeinn_scraper import TradeinnScraper

async def test_v2():
    scraper = TradeinnScraper()
    query = "masters of the universe origins"
    logger.info(f"🚀 Verificando TradeinnScraper V2 para: {query}")
    
    results = await scraper.search(query)
    
    if results:
        logger.success(f"✅ ÉXITO: Se encontraron {len(results)} productos.")
        for r in results[:5]:
            logger.info(f" - [{r.shop_name}] {r.product_name} | {r.price}€")
    else:
        logger.error("❌ FALLO: No se detectaron productos.")

if __name__ == "__main__":
    asyncio.run(test_v2())
