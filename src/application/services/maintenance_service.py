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
        Orquesta el mantenimiento FinOps de la base de datos:
        1. Consolida el historial detallado de price_history en product_monthly_stats con métricas avanzadas.
        2. Elimina ofertas de productos sin presencia actual en el mercado ("productos muertos").
        3. Purga el historial detallado antiguo (> 60 días) de productos activos ("productos vivos").
        4. Trunca logs extensos de scrapers antiguos (> 15 días).
        5. Purga exclusiones de la lista negra antiguas (> 90 días).
        
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
            
            # Fecha de corte para purga de historial (60 días)
            now = datetime.now(timezone.utc)
            history_cutoff = now - timedelta(days=60)
            
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
                    grouped_prices[key].append(price_val)
                
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
                
                # 2. Gestionar la purga de ofertas detalladas e historial
                # Comprobar si el producto tiene ofertas activas en el mercado actual
                active_offers = (
                    db.query(OfferModel)
                    .filter(
                        OfferModel.product_id == product.id,
                        OfferModel.is_available == True
                    )
                    .count()
                )
                
                if active_offers == 0:
                    # PRODUCTO MUERTO: Ya no hay ofertas activas.
                    # Purgamos todas sus ofertas obsoletas e historiales (por cascada delete-orphan).
                    deleted_offers_count = (
                        db.query(OfferModel)
                        .filter(OfferModel.product_id == product.id)
                        .delete(synchronize_session=False)
                    )
                    stats["offers_purged"] += deleted_offers_count
                else:
                    # PRODUCTO VIVO: Tiene ofertas activas.
                    # Mantenemos las ofertas actuales y purgamos el historial price_history detallado antiguo (> 60 días).
                    deleted_history_count = (
                        db.query(PriceHistoryModel)
                        .filter(
                            PriceHistoryModel.recorded_at < history_cutoff,
                            PriceHistoryModel.offer_id.in_(
                                db.query(OfferModel.id).filter(OfferModel.product_id == product.id)
                            )
                        )
                        .delete(synchronize_session=False)
                    )
                    stats["price_history_purged"] += deleted_history_count
            
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
