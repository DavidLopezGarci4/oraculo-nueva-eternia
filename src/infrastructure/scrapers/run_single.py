import asyncio
import sys
import datetime
from vec3.dev.adapters import initialize_runtime
from src.infrastructure.scrapers.pipeline import ScrapingPipeline
from src.infrastructure.scrapers.action_toys_scraper import ActionToysScraper
from src.infrastructure.scrapers.fantasia_scraper import FantasiaScraper
from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
from src.infrastructure.scrapers.ebay_scraper import EbayScraper
from src.infrastructure.scrapers.ebay_us_scraper import EbayUSScraper
from src.infrastructure.scrapers.vinted_scraper import VintedScraper
from src.infrastructure.scrapers.wallapop_scraper import WallapopScraper
from src.core.logger import logger

# Initialize 3OX Runtime
initialize_runtime()

async def run_scraper(spider_name: str):
    logger.info(f"🚀 Launching scraper: {spider_name}")
    
    spiders = []
    if spider_name.lower() == "actiontoys":
        spiders.append(ActionToysScraper())
    elif spider_name.lower() == "fantasia":
        spiders.append(FantasiaScraper())
    elif spider_name.lower() == "electropolis":
        from src.infrastructure.scrapers.electropolis_scraper import ElectropolisScraper
        spiders.append(ElectropolisScraper())
    elif spider_name.lower() == "amazon":
        spiders.append(AmazonScraper())
    elif spider_name.lower() == "ebay":
        spiders.append(EbayScraper())
    elif spider_name.lower() == "ebay_us":
        spiders.append(EbayUSScraper())
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
    status_row.start_time = datetime.datetime.utcnow()
    status_row.items_scraped = 0
    db.commit()

    try:
        pipeline = ScrapingPipeline(spiders)
        
        # We use "auto" to let the spider decide the best scraping strategy
        results = await pipeline.run_product_search("auto")
        
        logger.info(f"💾 Persisting {len(results)} offers to database...")
        # Phase 44: Pasamos los nombres de las tiendas para sincronizar disponibilidad
        pipeline.update_database(results, shop_names=[s.shop_name for s in spiders])
        
        status_row.status = "completed"
        status_row.items_scraped = len(results)
        status_row.end_time = datetime.datetime.utcnow()
        db.commit()
        
        logger.success("✅ Cycle complete.")
    except Exception as e:
        status_row.status = "error"
        status_row.end_time = datetime.datetime.utcnow()
        db.commit()
        logger.error(f"❌ Scraper failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/scrapers/run_single.py <spider_name> [--scraper name]")
    else:
        # Simple extraction to handle --scraper ebay or just ebay
        spider = sys.argv[-1] 
        asyncio.run(run_scraper(spider))
