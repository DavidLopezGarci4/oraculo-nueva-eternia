
from sqlalchemy import text
from src.infrastructure.database_cloud import engine_cloud
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Migrator")

def migrate():
    with engine_cloud.connect() as conn:
        logger.info("Starting DNA DNA Segregation Migration (Phase 14)...")
        
        # 1. Add origin_category to pending_matches
        try:
            conn.execute(text("ALTER TABLE pending_matches ADD COLUMN origin_category VARCHAR DEFAULT 'retail'"))
            conn.commit()
            logger.info("Successfully added origin_category to pending_matches.")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                logger.info("origin_category already exists in pending_matches.")
            else:
                logger.error(f"Error migrating pending_matches: {e}")

        # 2. Add origin_category to offers
        try:
            conn.execute(text("ALTER TABLE offers ADD COLUMN origin_category VARCHAR DEFAULT 'retail'"))
            conn.commit()
            logger.info("Successfully added origin_category to offers.")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                logger.info("origin_category already exists in offers.")
            else:
                logger.error(f"Error migrating offers: {e}")
        
        logger.info("Migration finished.")

if __name__ == "__main__":
    migrate()
