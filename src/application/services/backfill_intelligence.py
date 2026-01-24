
import sys
import io
from sqlalchemy import text
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session

# 1. Asegurar UTF-8 para evitar errores de stream en el agente
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class IntelligenceBackfiller:
    def __init__(self, db: Session):
        self.db = db

    def backfill_price_history(self):
        """Versión optimizada para evitar terminación del agente."""
        logger.info("Iniciando Backfill optimizado...")
        
        # SQL Crudo para ser 10x más rápido y consumir 0 RAM de objetos
        # Esta consulta identifica qué ofertas necesitan un 'Seed Point'
        sql_check = text("""
            INSERT INTO price_history (offer_id, price, recorded_at, is_snapshot)
            SELECT o.id, o.price, COALESCE(o.first_seen_at, o.last_seen, NOW()), true
            FROM offers o
            LEFT JOIN price_history ph ON o.id = ph.offer_id
            WHERE o.product_id IS NOT NULL 
            AND ph.id IS NULL
        """)
        
        try:
            result = self.db.execute(sql_check)
            self.db.commit()
            count = result.rowcount
            logger.success(f"Backfill completado: {count} puntos inyectados vía SQL Directo.")
            return count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error crítico en ejecución SQL: {e}")
            raise e

    def normalize_legacy_dates(self):
        """Normalización en una sola transacción atómica."""
        query = text("UPDATE offers SET first_seen_at = last_seen WHERE first_seen_at IS NULL")
        try:
            self.db.execute(query)
            self.db.commit()
            logger.info("Fechas normalizadas.")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error normalizando fechas: {e}")
            return False

if __name__ == "__main__":
    from src.infrastructure.database_cloud import SessionCloud
    # Limitar el alcance de la sesión para liberar memoria inmediatamente
    with SessionCloud() as session:
        bf = IntelligenceBackfiller(session)
        bf.backfill_price_history()
        bf.normalize_legacy_dates()
