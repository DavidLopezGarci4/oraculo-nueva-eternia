from src.infrastructure.database_cloud import engine_cloud as engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration_phase39")

def migrate():
    columns_to_add = [
        # Table: offers
        ("offers", "sale_type", "VARCHAR DEFAULT 'Retail'"),
        ("offers", "expiry_at", "TIMESTAMP"),
        ("offers", "bids_count", "INTEGER DEFAULT 0"),
        ("offers", "time_left_raw", "VARCHAR"),
        
        # Table: pending_matches
        ("pending_matches", "sale_type", "VARCHAR DEFAULT 'Retail'"),
        ("pending_matches", "expiry_at", "TIMESTAMP"),
        ("pending_matches", "bids_count", "INTEGER DEFAULT 0"),
        ("pending_matches", "time_left_raw", "VARCHAR"),
        
        # Table: price_history
        ("price_history", "is_snapshot", "BOOLEAN DEFAULT FALSE"),
    ]
    
    with engine.connect() as conn:
        for table, column, col_type in columns_to_add:
            try:
                # Check if column exists
                check_query = text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = '{column}'
                """)
                result = conn.execute(check_query).scalar()
                
                if result == 0:
                    logger.info(f"Adding column '{column}' to table '{table}'...")
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                    conn.commit()
                else:
                    logger.info(f"Column '{column}' already exists in table '{table}'. Skipping.")
            except Exception as e:
                logger.error(f"Error adding {column} to {table}: {e}")
                conn.rollback()

if __name__ == "__main__":
    migrate()
