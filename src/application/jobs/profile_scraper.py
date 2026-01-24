import sys
import asyncio
import json
# Import Scrapers
from src.infrastructure.scrapers.frikiverso_scraper import FrikiversoScraper
from src.infrastructure.scrapers.fantasia_scraper import FantasiaScraper
from src.infrastructure.scrapers.pixelatoy_scraper import PixelatoyScraper
from src.infrastructure.scrapers.electropolis_scraper import ElectropolisScraper
from src.core.logger import logger

async def profile(scraper_name):
    spider = None
    if scraper_name.lower() == "frikiverso":
        spider = FrikiversoScraper()
    elif scraper_name.lower() == "fantasia":
        spider = FantasiaScraper()
    elif scraper_name.lower() == "pixelatoy":
        spider = PixelatoyScraper()
    elif scraper_name.lower() == "electropolis":
        spider = ElectropolisScraper()
    else:
        logger.error(f"❌ Unknown scraper: {scraper_name}")
        return

    logger.info(f"🔮 Profiling {spider.shop_name} (Dry Run)...")
    try:
        offers = await spider.search("auto")
        
        # Extract ONLY titles as requested
        titles = sorted([o.product_name for o in offers])
        
        filename = f"data/profile_{scraper_name}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(titles, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Simulation Complete. Saved {len(titles)} titles to {filename}")
        logger.info("ℹ️ No changes were made to the database.")
        
    except Exception as e:
        logger.error(f"❌ Error during profiling: {e}")

if __name__ == "__main__":
    # Default to frikiverso if not argument provided
    target = sys.argv[1] if len(sys.argv) > 1 else "frikiverso"
    asyncio.run(profile(target))
