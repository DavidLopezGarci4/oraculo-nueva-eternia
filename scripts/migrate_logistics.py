from src.infrastructure.database_cloud import SessionCloud
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    with SessionCloud() as db:
        try:
            logger.info("Añadiendo columna custom_fees...")
            db.execute(text("ALTER TABLE logistic_rules ADD COLUMN IF NOT EXISTS custom_fees FLOAT DEFAULT 0.0"))
            
            logger.info("Añadiendo columna strategy_key...")
            db.execute(text("ALTER TABLE logistic_rules ADD COLUMN IF NOT EXISTS strategy_key VARCHAR"))
            
            db.commit()
            logger.info("Migración completada con éxito.")
        except Exception as e:
            db.rollback()
            logger.error(f"Error en la migración: {e}")
            raise e

if __name__ == "__main__":
    migrate()
