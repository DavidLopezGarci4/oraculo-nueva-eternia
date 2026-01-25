import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
root_path = Path(__file__).resolve().parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from src.infrastructure.scrapers.pipeline import ScrapingPipeline
from src.infrastructure.scrapers.action_toys_scraper import ActionToysScraper
from src.infrastructure.scrapers.fantasia_scraper import FantasiaScraper
from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
from src.core.logger import logger

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
        pipeline.update_database(results)
        
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
        print("Usage: python src/scrapers/run_single.py <spider_name>")
    else:
        asyncio.run(run_scraper(sys.argv[1]))
