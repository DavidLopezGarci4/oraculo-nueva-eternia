from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ScraperStatusModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cleanup")

def cleanup_duplicates():
    with SessionCloud() as db:
        # Get all scrapers
        scrapers = db.query(ScraperStatusModel).all()
        
        seen = {}
        duplicates = []
        
        for s in scrapers:
            name = s.spider_name
            if name in seen:
                duplicates.append(s)
            else:
                seen[name] = s
        
        if not duplicates:
            logger.info("No duplicate scrapers found.")
            return

        for dup in duplicates:
            logger.info(f"🗑️ Deleting duplicate scraper record: {dup.spider_name} (ID: {dup.id})")
            db.delete(dup)
        
        db.commit()
        logger.info("✅ Cleanup completed.")

if __name__ == "__main__":
    cleanup_duplicates()
