from sqlalchemy import text
from src.infrastructure.database_cloud import engine_cloud
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloud_migrator")

def migrate_cloud():
    print("--- INICIANDO MIGRACION DE ESQUEMA EN LA NUBE (DEAL SCORER) ---")
    
    tables = ["offers", "pending_matches"]
    
    with engine_cloud.connect() as conn:
        for table in tables:
            try:
                print(f"Adding 'opportunity_score' to {table} (Cloud)...")
                # Using standard SQL for PostgreSQL
                conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS opportunity_score INTEGER DEFAULT 0'))
                conn.commit()
                print(f"  Success or already exists in {table}.")
            except Exception as e:
                print(f"  Error migrating {table}: {e}")

    print("--- MIGRACION CLOUD COMPLETADA ---")

if __name__ == "__main__":
    migrate_cloud()
