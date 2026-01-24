import sys
import os
from pathlib import Path

# Add project root to Python path
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from src.infrastructure.database_cloud import SessionCloud as Session
from src.domain.models import ScraperStatusModel, ScraperExecutionLogModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cleanup_shops")

def cleanup_shops():
    shops_to_remove = ["MotuClassicsDE", "VendiloshopIT", "vendiloshopit", "Fantasia"]
    
    db = Session()
    try:
        # 1. Remove from ScraperStatusModel
        status_deleted = db.query(ScraperStatusModel).filter(
            ScraperStatusModel.scraper_name.in_(shops_to_remove)
        ).delete(synchronize_session=False)
        logger.info(f"🗑️ Removed {status_deleted} entries from scraper_status.")
        
        # 2. Remove from ScraperExecutionLogModel
        logs_deleted = db.query(ScraperExecutionLogModel).filter(
            ScraperExecutionLogModel.scraper_name.in_(shops_to_remove)
        ).delete(synchronize_session=False)
        logger.info(f"🗑️ Removed {logs_deleted} entries from scraper_execution_logs.")
        
        db.commit()
        logger.info("✨ Cleanup finished successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Cleanup failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_shops()
