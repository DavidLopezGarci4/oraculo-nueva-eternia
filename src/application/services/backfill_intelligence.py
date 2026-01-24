
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from src.domain.models import OfferModel, OfferHistoryModel, PriceHistoryModel, ProductModel
from loguru import logger

class IntelligenceBackfiller:
    def __init__(self, db: Session):
        self.db = db

    def backfill_price_history(self):
        """
        Migra logs de OfferHistoryModel a PriceHistoryModel para ofertas existentes.
        Esto permite que productos antiguos tengan gráficas de evolución.
        """
        logger.info("Iniciando Backfill de Inteligencia Histórica...")
        
        # 1. Obtener todas las ofertas actuales vinculadas
        offers = self.db.query(OfferModel).filter(OfferModel.product_id != None).all()
        
        migrated_count = 0
        for offer in offers:
            # 2. Buscar historial de esta URL
            history_logs = self.db.query(OfferHistoryModel).filter(
                OfferHistoryModel.offer_url == offer.url
            ).order_by(OfferHistoryModel.timestamp.asc()).all()
            
            if not history_logs:
                continue
                
            # Establecer first_seen_at si es nulo (basado en el primer log)
            if not offer.first_seen_at or offer.first_seen_at > history_logs[0].timestamp:
                offer.first_seen_at = history_logs[0].timestamp
                self.db.add(offer)

            for log in history_logs:
                # Verificar si ya existe un registro de precio para esa fecha/precio
                # Simplificación: No duplicar si el precio es igual en el mismo día
                exists = self.db.query(PriceHistoryModel).filter(
                    PriceHistoryModel.offer_id == offer.id,
                    PriceHistoryModel.price == log.price,
                ).first()
                
                if not exists:
                    ph = PriceHistoryModel(
                        offer_id=offer.id,
                        price=log.price,
                        recorded_at=log.timestamp,
                        is_snapshot=True # Marcamos como snapshot para que cuente en estadísticas
                    )
                    self.db.add(ph)
                    migrated_count += 1
        
        self.db.commit()
        logger.success(f"Backfill completado: {migrated_count} puntos de precio restaurados.")
        return migrated_count

    def normalize_legacy_dates(self):
        """
        Asegura que todos los productos y ofertas tengan fechas coherentes.
        """
        # Ofertas sin first_seen_at heredan de su creación o del primer log
        self.db.execute("UPDATE offers SET first_seen_at = last_seen WHERE first_seen_at IS NULL")
        self.db.commit()
        logger.info("Fechas de ofertas normalizadas.")

if __name__ == "__main__":
    from src.infrastructure.database_cloud import SessionCloud
    with SessionCloud() as session:
        backfiller = IntelligenceBackfiller(session)
        backfiller.backfill_price_history()
        backfiller.normalize_legacy_dates()
