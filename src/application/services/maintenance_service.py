import logging
import statistics
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from loguru import logger

from src.domain.models import (
    ProductModel,
    OfferModel,
    PriceHistoryModel,
    ProductMonthlyStatsModel,
    ScraperExecutionLogModel,
    BlackcludedItemModel,
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

        Optimizado en lotes (O(1) consultas SQL e I/O de disco) sin N+1 por producto u oferta.
        """
        logger.info("🧹 Iniciando proceso de compactación y mantenimiento de base de datos...")

        stats = {
            "products_processed": 0,
            "monthly_stats_saved": 0,
            "offers_purged": 0,
            "price_history_purged": 0,
            "logs_truncated": 0,
            "blacklist_purged": 0,
        }

        try:
            # 1. Contar todos los productos en 1 consulta ligera
            product_ids = [r[0] for r in db.query(ProductModel.id).all()]
            stats["products_processed"] = len(product_ids)

            now = datetime.now(timezone.utc)
            history_cutoff = now - timedelta(days=180)
            history_cutoff_naive = history_cutoff.replace(tzinfo=None)

            # 2. Cargar todo el historial de precios vinculado a productos en 1 sola consulta
            all_price_rows = (
                db.query(
                    OfferModel.product_id,
                    PriceHistoryModel.price,
                    PriceHistoryModel.recorded_at,
                    OfferModel.source_type,
                )
                .join(OfferModel, PriceHistoryModel.offer_id == OfferModel.id)
                .filter(OfferModel.product_id.isnot(None))
                .all()
            )

            grouped_prices: dict[tuple[int, int, int, str], list[float]] = {}
            for prod_id, price_val, recorded_at, source_type in all_price_rows:
                if not recorded_at or prod_id is None:
                    continue
                if recorded_at.tzinfo is None:
                    recorded_at = recorded_at.replace(tzinfo=timezone.utc)
                key = (prod_id, recorded_at.year, recorded_at.month, source_type or "Retail")
                grouped_prices.setdefault(key, []).append(float(price_val))

            # 3. Pre-cargar todas las estadísticas mensuales existentes en 1 sola consulta
            existing_stats_rows = db.query(ProductMonthlyStatsModel).all()
            existing_stats_map: dict[tuple[int, int, int, str], ProductMonthlyStatsModel] = {
                (s.product_id, s.year, s.month, s.source_type): s
                for s in existing_stats_rows
            }

            for (prod_id, year, month, source_type), price_list in grouped_prices.items():
                if not price_list:
                    continue

                count = len(price_list)
                avg_p = float(statistics.mean(price_list))
                median_p = float(statistics.median(price_list))
                min_p = float(min(price_list))
                max_p = float(max(price_list))

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

                stat_key = (prod_id, year, month, source_type)
                stat_record = existing_stats_map.get(stat_key)
                if not stat_record:
                    stat_record = ProductMonthlyStatsModel(
                        product_id=prod_id,
                        year=year,
                        month=month,
                        source_type=source_type,
                    )
                    db.add(stat_record)
                    existing_stats_map[stat_key] = stat_record
                else:
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

            # 4. Purga por lotes de ofertas inactivas e historial (> 6 meses)
            inactive_offers = (
                db.query(OfferModel)
                .filter(
                    OfferModel.product_id.isnot(None),
                    OfferModel.is_available == False,
                )
                .all()
            )
            inactive_offer_ids = [o.id for o in inactive_offers]

            if inactive_offer_ids:
                # Borrar historial antiguo en lotes de 500 IDs para compatibilidad SQLite/Postgres
                chunk_size = 500
                for i in range(0, len(inactive_offer_ids), chunk_size):
                    chunk = inactive_offer_ids[i : i + chunk_size]
                    deleted_history_count = (
                        db.query(PriceHistoryModel)
                        .filter(
                            PriceHistoryModel.offer_id.in_(chunk),
                            PriceHistoryModel.recorded_at < history_cutoff_naive,
                        )
                        .delete(synchronize_session=False)
                    )
                    stats["price_history_purged"] += deleted_history_count

                db.flush()

                # Identificar ofertas inactivas antiguas (> 180 días)
                old_inactive_offers = []
                for off in inactive_offers:
                    ref_date = off.last_seen or off.first_seen_at
                    if ref_date is not None and ref_date.tzinfo is None:
                        ref_date = ref_date.replace(tzinfo=timezone.utc)
                    if (ref_date is None) or (ref_date < history_cutoff):
                        old_inactive_offers.append(off)

                if old_inactive_offers:
                    old_inactive_ids = [o.id for o in old_inactive_offers]
                    offers_with_remaining_history: set[int] = set()
                    for i in range(0, len(old_inactive_ids), chunk_size):
                        chunk = old_inactive_ids[i : i + chunk_size]
                        rows = (
                            db.query(PriceHistoryModel.offer_id)
                            .filter(PriceHistoryModel.offer_id.in_(chunk))
                            .distinct()
                            .all()
                        )
                        offers_with_remaining_history.update(r[0] for r in rows)

                    offers_to_delete_ids = [
                        off.id
                        for off in old_inactive_offers
                        if off.id not in offers_with_remaining_history
                    ]
                    for i in range(0, len(offers_to_delete_ids), chunk_size):
                        chunk = offers_to_delete_ids[i : i + chunk_size]
                        deleted_offers = (
                            db.query(OfferModel)
                            .filter(OfferModel.id.in_(chunk))
                            .delete(synchronize_session=False)
                        )
                        stats["offers_purged"] += deleted_offers

            # 5. Truncar logs de scrapers antiguos (> 15 días)
            logs_cutoff = now - timedelta(days=15)
            logs_to_truncate = (
                db.query(ScraperExecutionLogModel)
                .filter(
                    ScraperExecutionLogModel.start_time < logs_cutoff,
                    ScraperExecutionLogModel.logs != None,
                    ScraperExecutionLogModel.logs != "Logs consolidados y purgados por mantenimiento FinOps.",
                )
                .all()
            )

            for log_record in logs_to_truncate:
                log_record.logs = "Logs consolidados y purgados por mantenimiento FinOps."
                stats["logs_truncated"] += 1

            # 6. Limpiar lista negra antigua (> 90 días)
            blacklist_cutoff = now - timedelta(days=90)
            deleted_blacklist_count = (
                db.query(BlackcludedItemModel)
                .filter(BlackcludedItemModel.created_at < blacklist_cutoff)
                .delete(synchronize_session=False)
            )
            stats["blacklist_purged"] += deleted_blacklist_count

            db.commit()

            try:
                from src.application.services.market_analytics_service import MarketAnalyticsService
                MarketAnalyticsService.invalidate_market_index_cache()
            except Exception:
                pass

            logger.info("✅ Compactación y mantenimiento de base de datos completados con éxito.")
            logger.info(f"Resumen de Optimización: {stats}")
            return stats

        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error durante el mantenimiento de base de datos: {e}")
            raise e
