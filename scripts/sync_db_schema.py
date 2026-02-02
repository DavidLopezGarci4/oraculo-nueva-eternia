
import sqlite3
from sqlalchemy import text
from src.infrastructure.database_cloud import engine_cloud, SessionCloud
from src.core.config import settings
from loguru import logger

def sync_local_db():
    logger.info("🛠️  Patcher: Checking LOCAL SQLite (oraculo.db)...")
    try:
        conn = sqlite3.connect("oraculo.db")
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(products);")
        columns = [col[1] for col in cursor.fetchall()]
        
        missing_columns = {
            "popularity_score": "INTEGER DEFAULT 0",
            "market_momentum": "FLOAT DEFAULT 1.0",
            "asin": "TEXT",
            "upc": "TEXT"
        }
        
        for col_name, col_def in missing_columns.items():
            if col_name not in columns:
                logger.info(f"   + Adding '{col_name}' to local database...")
                cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_def};")
        
        conn.commit()
        conn.close()
        logger.success("✅ Local database schema is UP TO DATE.")
    except Exception as e:
        logger.error(f"❌ Local patcher failed: {e}")

def sync_cloud_db():
    logger.info("🛠️  Patcher: Checking CLOUD Supabase/Postgres...")
    try:
        with engine_cloud.connect() as conn:
            # Check existing columns using information_schema
            query = text("SELECT column_name FROM information_schema.columns WHERE table_name = 'products'")
            result = conn.execute(query)
            columns = [row[0] for row in result]
            
            missing_columns = {
                "popularity_score": "INTEGER DEFAULT 0",
                "market_momentum": "FLOAT DEFAULT 1.0",
                "asin": "VARCHAR",
                "upc": "VARCHAR"
            }
            
            # Use a transaction for the cloud
            for col_name, col_def in missing_columns.items():
                if col_name not in columns:
                    logger.info(f"   + Adding '{col_name}' to cloud database...")
                    # ALTER TABLE requires separate execution in some dialects
                    conn.execute(text(f"ALTER TABLE products ADD COLUMN {col_name} {col_def}"))
            
            conn.commit()
            logger.success("✅ Cloud database schema is UP TO DATE.")
    except Exception as e:
        logger.error(f"❌ Cloud patcher failed: {e}")

if __name__ == "__main__":
    sync_local_db()
    sync_cloud_db()
