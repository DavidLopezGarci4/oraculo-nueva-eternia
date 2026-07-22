import asyncio
import sys
import os
import datetime

# Dynamic Sys Path injection for absolute safety - prioritizing .3ox to avoid local vec3 folder collision
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
sys.path.insert(0, os.path.join(root_dir, ".3ox"))
sys.path.insert(1, root_dir)

from src.infrastructure.scrapers.pipeline import ScrapingPipeline
from src.infrastructure.scrapers.fantasia_scraper import FantasiaScraper
from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
from src.infrastructure.scrapers.ebay_scraper import EbayScraper
from src.infrastructure.scrapers.vinted_scraper import VintedScraper
from src.infrastructure.scrapers.wallapop_scraper import WallapopScraper
from src.core.logger import logger

try:
    from vec3.dev.adapters import initialize_runtime
    # Initialize 3OX Runtime
    initialize_runtime()
except ImportError:
    logger.warning("⚠️ vec3.dev.adapters not found, continuing without initialize_runtime")



async def run_scraper(spider_name: str, search_query: str = "auto"):
    logger.info(f"🚀 Launching scraper: {spider_name} with query: {search_query}")
    
    spiders = []
    if spider_name.lower() == "fantasia":
        spiders.append(FantasiaScraper())
    elif spider_name.lower() == "electropolis":
        from src.infrastructure.scrapers.electropolis_scraper import ElectropolisScraper
        spiders.append(ElectropolisScraper())
    elif spider_name.lower() == "amazon":
        spiders.append(AmazonScraper())
    elif spider_name.lower() == "ebay":
        spiders.append(EbayScraper())
    elif spider_name.lower() == "vinted":
        spiders.append(VintedScraper())
    elif spider_name.lower() == "wallapop":
        spiders.append(WallapopScraper())
    else:
        logger.error(f"Unknown scraper: {spider_name}")
        return

    # Scraper Status - Init
    from src.infrastructure.database import SessionLocal
    from src.domain.models import ScraperStatusModel
    import datetime
    
    db = SessionLocal()
    status_row = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == spider_name).first()
    if not status_row:
        status_row = ScraperStatusModel(spider_name=spider_name)
        db.add(status_row)
    
    status_row.status = "running"
    status_row.start_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    status_row.items_scraped = 0
    db.commit()

    try:
        pipeline = ScrapingPipeline(spiders)
        
        results = await pipeline.run_product_search(search_query)
        
        logger.info(f"💾 Persisting {len(results)} offers to database...")
        # Phase 44: Pasamos los nombres de las tiendas para sincronizar disponibilidad
        pipeline.update_database(results, shop_names=[s.shop_name for s in spiders])
        
        is_blocked = any(getattr(s, 'blocked', False) for s in spiders)
        if is_blocked:
            status_row.status = "blocked"
            status_row.items_scraped = 0
            status_row.end_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            db.commit()
            
            logger.error(f"🛡️ [BLOCKED] Scraper was blocked by anti-bot measures!")
            
            # Send Telegram alert for manual block visibility
            try:
                from src.core.notifier import NotifierService
                notifier = NotifierService()
                msg = f"⚠️ **INCURSIÓN MANUAL BLOQUEADA**\n\nEl scraper manual para **{spider_name}** ha sido detectado y bloqueado por cortafuegos (WAF/CloudFront)."
                await notifier.send_message(msg)
            except Exception as ne:
                logger.warning(f"Failed to send Telegram alert: {ne}")
        else:
            status_row.status = "completed"
            status_row.items_scraped = len(results)
            status_row.end_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            db.commit()
            logger.success("✅ Cycle complete.")
    except Exception as e:
        status_row.status = "error"
        status_row.end_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        db.commit()
        logger.error(f"❌ Scraper failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/scrapers/run_single.py <spider_name> [--search 'query']")
    else:
        spider = sys.argv[1]
        search = "auto"
        if "--search" in sys.argv:
            try:
                idx = sys.argv.index("--search")
                if idx + 1 < len(sys.argv):
                    search = sys.argv[idx + 1]
            except ValueError:
                pass
        asyncio.run(run_scraper(spider, search))
