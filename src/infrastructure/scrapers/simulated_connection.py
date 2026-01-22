import asyncio
import logging
import json
import datetime
from pathlib import Path
from typing import Dict, List

from src.infrastructure.scrapers.bbts_scraper import BigBadToyStoreScraper
from src.infrastructure.scrapers.detoyboys_scraper import DeToyboysNLScraper
from src.infrastructure.scrapers.action_toys_scraper import ActionToysScraper
from src.infrastructure.scrapers.toymi_scraper import ToymiEUScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("logs/connection_simulator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ConnectionSimulator")

async def check_connection(scraper_class) -> Dict:
    scraper = scraper_class()
    name = scraper.spider_name
    start_time = datetime.datetime.now()
    
    try:
        logger.info(f"Testing connection for: {name}...")
        # A minimal search or home page hit to verify "Human-like" connection
        # We use 'auto' which is the default for a category/search hit
        # We wrap it to ensure it only does 1 page for heartbeats
        scraper.max_pages = 1 
        results = await scraper.search("auto")
        
        duration = (datetime.datetime.now() - start_time).total_seconds()
        
        status = {
            "spider": name,
            "status": "ONLINE" if not getattr(scraper, 'blocked', False) else "BLOCKED",
            "items_found": len(results),
            "errors": getattr(scraper, 'errors', 0),
            "latency_sec": round(duration, 2),
            "timestamp": datetime.datetime.now().isoformat()
        }
        logger.info(f"[OK] {name}: {status['status']} ({len(results)} items) in {status['latency_sec']}s")
        return status
    except Exception as e:
        logger.error(f"[FAIL] {name}: FAILED - {e}")
        return {
            "spider": name,
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }

async def run_simulation():
    scrapers_to_test = [
        BigBadToyStoreScraper,
        DeToyboysNLScraper,
        ActionToysScraper,
        ToymiEUScraper
    ]
    
    logger.info("Starting Simulated Background Connection Check...")
    
    reports = []
    # Run in parallel to simulate background pressure
    tasks = [check_connection(s) for s in scrapers_to_test]
    reports = await asyncio.gather(*tasks)
    
    # Save report
    report_path = Path("logs/scraper_heartbeat.json")
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(reports, f, indent=4)
    
    logger.info(f"Global report saved to {report_path}")

if __name__ == "__main__":
    asyncio.run(run_simulation())
