import logging
from sqlalchemy import text, inspect
from src.infrastructure.database import engine as engine_local
from src.infrastructure.database_cloud import engine_cloud
from src.domain.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("universal_migrator")

def migrate():
    """
    Intelligently synchronizes DB schema for both SQLite and Postgres.
    Does NOT use Alembic to maintain project simplicity but ensures reliability.
    """
    logger.info("Starting Universal Migration...")
    
    # 1. Sync Local Database
    _sync_engine(engine_local, "Local")
    
    # 2. Sync Cloud Database (if configured)
    if engine_cloud and "sqlite" not in str(engine_cloud.url):
        _sync_engine(engine_cloud, "Cloud")
    else:
        logger.info("Skipping Cloud Sync (No Cloud DB configured or is SQLite).")

    logger.info("Universal Migration finished successfully.")

def _sync_engine(engine, label: str):
    """Internal helper to sync a specific engine."""
    logger.info(f"--- Synchronizing {label} Engine ---")
    inspector = inspect(engine)
    
    # Tables to check
    tables = inspector.get_table_names()
    
    # A. Ensure all tables exist in Base.metadata
    Base.metadata.create_all(bind=engine)
    logger.info(f"[{label}] Core tables checked/created.")

    # B. Check for missing columns in existing tables
    with engine.connect() as conn:
        # --- Table: products ---
        columns_products = [c['name'] for c in inspector.get_columns("products")]
        if "ean" not in columns_products:
            logger.info("Adding 'ean' to products table...")
            try:
                conn.execute(text("ALTER TABLE products ADD COLUMN ean VARCHAR(50) UNIQUE"))
                conn.commit()
            except Exception as e:
                logger.warning(f"Could not add ean: {e}")

        # --- Table: offers ---
        columns_offers = [c['name'] for c in inspector.get_columns("offers")]
        if "currency" not in columns_offers:
            logger.info("Adding 'currency' to offers table...")
            conn.execute(text("ALTER TABLE offers ADD COLUMN currency VARCHAR(10) DEFAULT 'EUR'"))
            conn.commit()
            
        if "min_price" not in columns_offers:
            logger.info("Adding 'min_price' to offers table...")
            conn.execute(text("ALTER TABLE offers ADD COLUMN min_price FLOAT DEFAULT 0.0"))
            conn.commit()

        if "max_price" not in columns_offers:
            logger.info("Adding 'max_price' to offers table...")
            conn.execute(text("ALTER TABLE offers ADD COLUMN max_price FLOAT DEFAULT 0.0"))
            conn.commit()

            conn.execute(text("ALTER TABLE offers ADD COLUMN origin_category VARCHAR(20) DEFAULT 'retail'"))
            conn.commit()

        if "first_seen_at" not in columns_offers:
            logger.info("Adding 'first_seen_at' to offers table...")
            conn.execute(text("ALTER TABLE offers ADD COLUMN first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
            conn.commit()

        if "sold_at" not in columns_offers:
            logger.info("Adding 'sold_at' to offers table...")
            conn.execute(text("ALTER TABLE offers ADD COLUMN sold_at TIMESTAMP NULL"))
            conn.commit()

        if "is_sold" not in columns_offers:
            logger.info("Adding 'is_sold' to offers table...")
            conn.execute(text("ALTER TABLE offers ADD COLUMN is_sold BOOLEAN DEFAULT FALSE"))
            conn.commit()

        if "original_listing_date" not in columns_offers:
            logger.info("Adding 'original_listing_date' to offers table...")
            conn.execute(text("ALTER TABLE offers ADD COLUMN original_listing_date TIMESTAMP NULL"))
            conn.commit()

        if "last_price_update" not in columns_offers:
            logger.info("Adding 'last_price_update' to offers table...")
            conn.execute(text("ALTER TABLE offers ADD COLUMN last_price_update TIMESTAMP NULL"))
            conn.commit()

        # --- Table: pending_matches ---
        columns_pending = [c['name'] for c in inspector.get_columns("pending_matches")]
        if "ean" not in columns_pending:
            logger.info("Adding 'ean' to pending_matches table...")
            try:
                conn.execute(text("ALTER TABLE pending_matches ADD COLUMN ean VARCHAR(50)"))
                conn.commit()
            except Exception as e:
                logger.warning(f"Could not add ean to pending_matches: {e}")

            conn.execute(text("ALTER TABLE pending_matches ADD COLUMN origin_category VARCHAR(20) DEFAULT 'retail'"))
            conn.commit()

        if "first_seen_at" not in columns_pending:
            logger.info("Adding 'first_seen_at' to pending_matches table...")
            conn.execute(text("ALTER TABLE pending_matches ADD COLUMN first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
            conn.commit()

        if "sold_at" not in columns_pending:
            logger.info("Adding 'sold_at' to pending_matches table...")
            conn.execute(text("ALTER TABLE pending_matches ADD COLUMN sold_at TIMESTAMP NULL"))
            conn.commit()

        if "is_sold" not in columns_pending:
            logger.info("Adding 'is_sold' to pending_matches table...")
            conn.execute(text("ALTER TABLE pending_matches ADD COLUMN is_sold BOOLEAN DEFAULT FALSE"))
            conn.commit()

        if "original_listing_date" not in columns_pending:
            logger.info("Adding 'original_listing_date' to pending_matches table...")
            conn.execute(text("ALTER TABLE pending_matches ADD COLUMN original_listing_date TIMESTAMP NULL"))
            conn.commit()

        if "last_price_update" not in columns_pending:
            logger.info("Adding 'last_price_update' to pending_matches table...")
            conn.execute(text("ALTER TABLE pending_matches ADD COLUMN last_price_update TIMESTAMP NULL"))
            conn.commit()

        # --- Table: price_alerts (Created by create_all, but check for created_at if old) ---
        # (Assuming it's new so skip for now)

        # --- Table: blackcluded_items (Check for all columns) ---
        if "blackcluded_items" in inspector.get_table_names():
             columns_black = [c['name'] for c in inspector.get_columns("blackcluded_items")]
             
             if "source_type" not in columns_black:
                 logger.info(f"[{label}] Adding 'source_type' to blackcluded_items...")
                 conn.execute(text("ALTER TABLE blackcluded_items ADD COLUMN source_type VARCHAR(50) DEFAULT 'Retail'"))
                 conn.commit()

             if "reason" not in columns_black:
                 logger.info(f"[{label}] Adding 'reason' to blackcluded_items...")
                 conn.execute(text("ALTER TABLE blackcluded_items ADD COLUMN reason TEXT"))
                 conn.commit()
                 
             if "validation_status" not in columns_black:
                 logger.info(f"[{label}] Adding 'validation_status' to blackcluded_items...")
                 conn.execute(text("ALTER TABLE blackcluded_items ADD COLUMN validation_status VARCHAR(50) DEFAULT 'VALIDATED'"))
                 conn.commit()

             if "anomaly_flags" not in columns_black:
                 logger.info(f"[{label}] Adding 'anomaly_flags' to blackcluded_items...")
                 conn.execute(text("ALTER TABLE blackcluded_items ADD COLUMN anomaly_flags TEXT"))
                 conn.commit()
                 
             if "is_blocked" not in columns_black:
                 logger.info(f"[{label}] Adding 'is_blocked' to blackcluded_items...")
                 conn.execute(text("ALTER TABLE blackcluded_items ADD COLUMN is_blocked BOOLEAN DEFAULT FALSE"))
                 conn.commit()
                 
             if "created_at" not in columns_black:
                 logger.info(f"[{label}] Adding 'created_at' to blackcluded_items...")
                 conn.execute(text("ALTER TABLE blackcluded_items ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                 conn.commit()

        # --- Terminology Audit: Fix regressions and ensure 'spider_name' ---
        # Note: If someone accidentally renamed to scraper_name, we undo it here.
        rename_targets = [
            ("scraper_status", "scraper_name", "spider_name"),
            ("scraper_execution_logs", "scraper_name", "spider_name"),
            ("kaizen_insights", "scraper_name", "spider_name")
        ]

        for table, old_col, new_col in rename_targets:
            if table in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns(table)]
                if old_col in cols and new_col not in cols:
                    logger.info(f"[{label}] Renaming column in '{table}': '{old_col}' -> '{new_col}'...")
                    try:
                        # Standard SQL for renaming (Works on Postgres and recent SQLite)
                        conn.execute(text(f'ALTER TABLE "{table}" RENAME COLUMN "{old_col}" TO "{new_col}"'))
                        conn.commit()
                        logger.info(f"[{label}] Table '{table}' column '{new_col}' rename successful.")
                    except Exception as e:
                        logger.error(f"[{label}] Failed to rename column in '{table}': {e}")
                        conn.rollback()

if __name__ == "__main__":
    migrate()
