from src.infrastructure.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    commands = [
        # 1. ProductModel
        "ALTER TABLE products ADD COLUMN avg_market_price FLOAT;",
        "ALTER TABLE products ADD COLUMN p25_price FLOAT;",
        "ALTER TABLE products ADD COLUMN master_image_hash VARCHAR;",
        
        # 2. OfferModel
        "ALTER TABLE offers ADD COLUMN validation_status VARCHAR DEFAULT 'VALIDATED';",
        "ALTER TABLE offers ADD COLUMN anomaly_flags VARCHAR;",
        "ALTER TABLE offers ADD COLUMN is_blocked BOOLEAN DEFAULT FALSE;",
        
        # 3. PendingMatchModel
        "ALTER TABLE pending_matches ADD COLUMN validation_status VARCHAR DEFAULT 'PENDING';",
        "ALTER TABLE pending_matches ADD COLUMN anomaly_flags VARCHAR;",
        "ALTER TABLE pending_matches ADD COLUMN is_blocked BOOLEAN DEFAULT FALSE;"
    ]
    
    with engine.connect() as conn:
        for cmd in commands:
            try:
                conn.execute(text(cmd))
                conn.commit()
                logger.info(f"Executed: {cmd}")
            except Exception as e:
                logger.debug(f"Skipped (likely exists): {cmd}")

if __name__ == "__main__":
    migrate()
