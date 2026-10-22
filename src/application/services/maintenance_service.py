import logging
import statistics
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from loguru import logger
from sqlalchemy import select, delete, and_

from src.domain.models import (
    ProductModel,
    OfferModel,
    PriceHistoryModel,
    ProductMonthlyStatsModel,
    ScraperExecutionLogModel,
    BlackcludedItemModel
)

class MaintenanceService:
    @staticmethod
    def compact_database(db) -> Dict[str, Any]:
        """
        Orquesta el mantenimiento FinOps de la base de datos (Ventana Hot = 6 meses / 180 días):
        1. Consolida el historial detallado de price_history en product_monthly_stats con métricas avanzadas (IQR, mediana, P25/P75).
        2. Preserva intactas las ofertas con link activo (is_available=True) y su historial para mantener accesibilidad y trazabilidad.
        3. Conserva durante 6 meses (180 días) el historial granular de ofertas inactivas para alimentar las curvas de 1M, 3M y 6M.
        4. Purga el historial detallado (> 180 días) de ofertas inactivas y elimina las ofertas inactivas obsoletas (> 180 días).
        5. Trunca logs extensos de scrapers antiguos (> 15 días) y exclusiones antiguas (> 90 días).
        
        Retorna estadísticas detalladas del proceso.
        """
        logger.info("🧹 Iniciando proceso de compactación y mantenimiento de base de datos...")
        
        stats = {
            "products_processed": 0,
            "monthly_stats_saved": 0,
            "offers_purged": 0,
            "price_history_purged": 0,
            "logs_truncated": 0,
            "blacklist_purged": 0
        }
        
        try:
            # 1. Obtener todos los productos
            products = db.query(ProductModel).all()
            stats["products_processed"] = len(products)
            
            # Fecha de corte para compactación de historial: 6 meses (180 días)
            now = datetime.now(timezone.utc)
            history_cutoff = now - timedelta(days=180)
            history_cutoff_naive = history_cutoff.replace(tzinfo=None)
            
            for product in products:
                # Obtener todos los precios históricos de este producto
                prices_query = (
                    db.query(
                        PriceHistoryModel.price,
                        PriceHistoryModel.recorded_at,
                        OfferModel.source_type
                    )
                    .join(OfferModel, PriceHistoryModel.offer_id == OfferModel.id)
                    .filter(OfferModel.product_id == product.id)
                    .all()
                )
                
                # Agrupar precios por año, mes y tipo de canal (Retail / P2P)
                grouped_prices = {}
                for price_val, recorded_at, source_type in prices_query:
                    if not recorded_at:
                        continue
                    # Asegurar zona horaria UTC
                    if recorded_at.tzinfo is None:
                        recorded_at = recorded_at.replace(tzinfo=timezone.utc)
                        
                    key = (recorded_at.year, recorded_at.month, source_type or "Retail")
                    if key not in grouped_prices:
                        grouped_prices[key] = []
                    grouped_prices[key].append(float(price_val))
                
                # Calcular y guardar estadísticas mensuales consolidadas
                for (year, month, source_type), price_list in grouped_prices.items():
                    if not price_list:
                        continue
                    
                    count = len(price_list)
                    avg_p = float(statistics.mean(price_list))
                    median_p = float(statistics.median(price_list))
                    min_p = float(min(price_list))
                    max_p = float(max(price_list))
                    
                    # Cálculo de métricas avanzadas (mínimo 2 muestras)
                    if count >= 2:
                        try:
                            std_dev = float(statistics.stdev(price_list))
                        except Exception:
                            std_dev = 0.0
                            
                        try:
                            q = statistics.quantiles(price_list, n=4)
                            p25 = float(q[0])
                            p75 = float(q[2])
                        except Exception:
                            p25 = avg_p
                            p75 = avg_p
                    else:
                        std_dev = 0.0
                        p25 = price_list[0]
                        p75 = price_list[0]
                        
                    # Buscar si ya existe la fila en la tabla agregada
                    stat_record = db.query(ProductMonthlyStatsModel).filter(
                        and_(
                            ProductMonthlyStatsModel.product_id == product.id,
                            ProductMonthlyStatsModel.year == year,
                            ProductMonthlyStatsModel.month == month,
                            ProductMonthlyStatsModel.source_type == source_type
                        )
                    ).first()
                    
                    if not stat_record:
                        stat_record = ProductMonthlyStatsModel(
                            product_id=product.id,
                            year=year,
                            month=month,
                            source_type=source_type
                        )
                        db.add(stat_record)
                    else:
                        # Evitar que una re-ejecución sobre un mes ya compactado (con menos muestras vivas)
                        # degrade o sobrescriba la estadística consolidada previa
                        existing_count = stat_record.offers_count or 0
                        if count < existing_count:
                            continue
                        
                    stat_record.avg_price = avg_p
                    stat_record.median_price = median_p
                    stat_record.min_price = min_p
                    stat_record.max_price = max_p
                    stat_record.std_dev_price = std_dev
                    stat_record.p25_price = p25
                    stat_record.p75_price = p75
                    stat_record.offers_count = count
                    stat_record.updated_at = now
                    
                    stats["monthly_stats_saved"] += 1
                
                # Commiteamos los acumulados mensuales por producto para liberar memoria
                db.commit()
                
                # 2. Gestionar la purga de ofertas inactivas e historial (> 6 meses)
                # Las ofertas con link activo (is_available == True) NUNCA se compactan ni se borran.
                inactive_offer_ids = [
                    r[0] for r in db.query(OfferModel.id).filter(
                        OfferModel.product_id == product.id,
                        OfferModel.is_available == False
                    ).all()
                ]
                
                if inactive_offer_ids:
                    # Purgar historial detallado > 180 días perteneciente únicamente a ofertas inactivas
                    deleted_history_count = (
                        db.query(PriceHistoryModel)
                        .filter(
                            PriceHistoryModel.offer_id.in_(inactive_offer_ids),
                            PriceHistoryModel.recorded_at < history_cutoff_naive
                        )
                        .delete(synchronize_session=False)
                    )
                    stats["price_history_purged"] += deleted_history_count
                    db.flush()
                    
                    # Eliminar ofertas inactivas cuya última actividad supere los 180 días
                    # y que ya no tengan registros recientes en price_history
                    inactive_offers = (
                        db.query(OfferModel)
                        .filter(OfferModel.id.in_(inactive_offer_ids))
                        .all()
                    )
                    for off in inactive_offers:
                        ref_date = off.last_seen or off.first_seen_at
                        if ref_date is not None and ref_date.tzinfo is None:
                            ref_date = ref_date.replace(tzinfo=timezone.utc)
                        is_old_offer = (ref_date is None) or (ref_date < history_cutoff)
                        if is_old_offer:
                            remaining_hist = (
                                db.query(PriceHistoryModel.id)
                                .filter(PriceHistoryModel.offer_id == off.id)
                                .count()
                            )
                            if remaining_hist == 0:
                                db.delete(off)
                                stats["offers_purged"] += 1
            
            db.commit()
            
            # 3. Truncar logs de scrapers antiguos (> 15 días)
            logs_cutoff = now - timedelta(days=15)
            logs_to_truncate = (
                db.query(ScraperExecutionLogModel)
                .filter(
                    ScraperExecutionLogModel.start_time < logs_cutoff,
                    ScraperExecutionLogModel.logs != None,
                    ScraperExecutionLogModel.logs != "Logs consolidados y purgados por mantenimiento FinOps."
                )
                .all()
            )
            
            for log_record in logs_to_truncate:
                log_record.logs = "Logs consolidados y purgados por mantenimiento FinOps."
                stats["logs_truncated"] += 1
                
            if logs_to_truncate:
                db.commit()
                
            # 4. Limpiar lista negra antigua (> 90 días)
            blacklist_cutoff = now - timedelta(days=90)
            deleted_blacklist_count = (
                db.query(BlackcludedItemModel)
                .filter(BlackcludedItemModel.created_at < blacklist_cutoff)
                .delete(synchronize_session=False)
            )
            stats["blacklist_purged"] += deleted_blacklist_count
            
            db.commit()
            
            logger.info("✅ Compactación y mantenimiento de base de datos completados con éxito.")
            logger.info(f"Resumen de Optimización: {stats}")
            return stats
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error durante el mantenimiento de base de datos: {e}")
            raise e
