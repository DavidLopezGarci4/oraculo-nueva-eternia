from src.infrastructure.database_cloud import engine_cloud
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    commands = [
        # 1. ProductModel: master_image_hash
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS master_image_hash VARCHAR;",
        
        # 2. OfferModel: validation_status, anomaly_flags, is_blocked
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS validation_status VARCHAR DEFAULT 'VALIDATED';",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS anomaly_flags VARCHAR;",
        "ALTER TABLE offers ADD COLUMN IF NOT EXISTS is_blocked BOOLEAN DEFAULT FALSE;",
        
        # 3. PendingMatchModel: validation_status, anomaly_flags, is_blocked
        "ALTER TABLE pending_matches ADD COLUMN IF NOT EXISTS validation_status VARCHAR DEFAULT 'PENDING';",
        "ALTER TABLE pending_matches ADD COLUMN IF NOT EXISTS anomaly_flags VARCHAR;",
        "ALTER TABLE pending_matches ADD COLUMN IF NOT EXISTS is_blocked BOOLEAN DEFAULT FALSE;"
    ]
    
    with engine_cloud.connect() as conn:
        for cmd in commands:
            try:
                conn.execute(text(cmd))
                conn.commit()
                logger.info(f"Executed: {cmd}")
            except Exception as e:
                logger.error(f"Failed: {cmd} - {e}")

if __name__ == "__main__":
    migrate()
