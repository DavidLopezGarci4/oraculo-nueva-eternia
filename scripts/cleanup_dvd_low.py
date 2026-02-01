from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ScraperStatusModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cleanup")

def cleanup_specific_duplicates():
    with SessionCloud() as db:
        # Purge lowercase version
        target = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == 'dvdstorespain').first()
        if target:
            logger.info(f"🗑️ Deleting lowercase scraper record: {target.spider_name} (ID: {target.id})")
            db.delete(target)
            db.commit()
            logger.info("✅ Cleanup completed.")
        else:
            logger.info("No lowercase 'dvdstorespain' found.")

if __name__ == "__main__":
    cleanup_specific_duplicates()
