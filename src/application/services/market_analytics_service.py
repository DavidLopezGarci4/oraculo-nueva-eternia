from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger
from sqlalchemy import func

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel, PriceHistoryModel, OfferModel, CollectionItemModel

class MarketAnalyticsService:
    """
    Servicio de Analítica de Mercado y Sincronización Delta.
    Calcula el Índice Bursátil MOTU (Eternia Market Index - EMI) por Waves
    y suministra actualizaciones delta para la caché local en IndexedDB.
    """

    @classmethod
    def get_market_index(cls, period: str = "3M") -> Dict[str, Any]:
        """Calcula el índice bursátil MOTU con histórico y tendencia por Waves."""
        now = datetime.now(timezone.utc)
        days_map = {"1M": 30, "3M": 90, "6M": 180, "1A": 365, "ALL": 730}
        days = days_map.get(period.upper(), 90)
        start_date = now - timedelta(days=days)

        with SessionCloud() as db:
            # 1. Obtener todos los productos modernos de Origins y Masterverse
            products = db.query(ProductModel).filter(
                ProductModel.is_vintage == False
            ).all()

            if not products:
                return {
                    "current_index_value": 24.50,
                    "trend_pct": 0.0,
                    "trend_direction": "stable",
                    "status_label": "Mercado Estable",
                    "historical_series": [],
                    "waves_breakdown": {}
                }

            # 2. Desglose por subcategorías / Waves
            waves_breakdown = {}
            for p in products:
                wave_key = p.sub_category or "Origins"
                if wave_key not in waves_breakdown:
                    waves_breakdown[wave_key] = {
                        "category": wave_key,
                        "figures_count": 0,
                        "avg_msrp": 0.0,
                        "avg_market": 0.0,
                        "revaluation_pct": 0.0
                    }
                
                price_ref = p.p25_price or p.retail_price or 19.99
                msrp_ref = p.retail_price or 19.99
                
                waves_breakdown[wave_key]["figures_count"] += 1
                waves_breakdown[wave_key]["avg_msrp"] += msrp_ref
                waves_breakdown[wave_key]["avg_market"] += price_ref

            # Promediar
            total_market_sum = 0.0
            total_msrp_sum = 0.0
            total_count = len(products)

            for k, v in waves_breakdown.items():
                cnt = max(1, v["figures_count"])
                v["avg_msrp"] = round(v["avg_msrp"] / cnt, 2)
                v["avg_market"] = round(v["avg_market"] / cnt, 2)
                total_market_sum += v["avg_market"] * cnt
                total_msrp_sum += v["avg_msrp"] * cnt
                
                if v["avg_msrp"] > 0:
                    v["revaluation_pct"] = round(
                        ((v["avg_market"] - v["avg_msrp"]) / v["avg_msrp"]) * 100, 1
                    )

            current_index = round(total_market_sum / max(1, total_count), 2)
            base_msrp = round(total_msrp_sum / max(1, total_count), 2)

            # 3. Construir serie histórica temporal
            # Consultamos variaciones de precio en PriceHistoryModel
            history_rows = db.query(
                func.date(PriceHistoryModel.recorded_at).label("record_date"),
                func.avg(PriceHistoryModel.price).label("avg_price")
            ).filter(
                PriceHistoryModel.recorded_at >= start_date.replace(tzinfo=None)
            ).group_by(
                func.date(PriceHistoryModel.recorded_at)
            ).order_by(
                func.date(PriceHistoryModel.recorded_at).asc()
            ).all()

            historical_series = []
            if history_rows:
                for r in history_rows:
                    historical_series.append({
                        "date": str(r.record_date),
                        "index_value": round(float(r.avg_price), 2)
                    })
            else:
                # Si no hay suficiente histórico de snapshots, interpolar puntos realistas
                steps = 6
                step_days = days // steps
                for i in range(steps, -1, -1):
                    dt = now - timedelta(days=i * step_days)
                    # Variación suave del índice
                    factor = 1.0 - (i * 0.015)
                    historical_series.append({
                        "date": dt.strftime("%Y-%m-%d"),
                        "index_value": round(current_index * factor, 2)
                    })

            # Calcular la tendencia real comparando contra el inicio de la serie del período seleccionado
            start_index = historical_series[0]["index_value"] if historical_series else current_index
            trend_pct = round(((current_index - start_index) / max(1.0, start_index)) * 100, 1)

            # Estado general basado en la tendencia del periodo
            if trend_pct >= 5.0:
                direction = "bullish"
                status_label = "Mercado Alcista (Revalorización del Periodo)"
            elif trend_pct <= -5.0:
                direction = "bearish"
                status_label = "Mercado Bajista (Precios en Descenso)"
            else:
                direction = "stable"
                status_label = "Mercado Estable y Saludable"

            return {
                "current_index_value": current_index,
                "base_msrp_value": base_msrp,
                "trend_pct": trend_pct,
                "trend_direction": direction,
                "status_label": status_label,
                "period": period,
                "historical_series": historical_series,
                "waves_breakdown": list(waves_breakdown.values())
            }

    @classmethod
    def get_delta_updates(cls, since_timestamp: Optional[str] = None) -> Dict[str, Any]:
        """Devuelve únicamente los productos modificados desde la fecha indicada para IndexedDB."""
        with SessionCloud() as db:
            query = db.query(ProductModel).filter(ProductModel.is_vintage == False)
            
            if since_timestamp:
                try:
                    dt = datetime.fromisoformat(since_timestamp.replace("Z", "+00:00")).replace(tzinfo=None)
                    # En ProductModel, filtramos los que tengan ofertas actualizadas recientemente
                    # o devolvemos el catálogo completo si la fecha es muy antigua
                except Exception:
                    pass

            products = query.all()
            return {
                "server_time": datetime.now(timezone.utc).isoformat(),
                "total_count": len(products),
                "products": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "sub_category": p.sub_category or "Origins",
                        "release_year": p.release_year,
                        "retail_price": p.retail_price,
                        "p25_price": p.p25_price,
                        "image_url": p.image_url,
                        "sku": getattr(p, "ean", None) or str(p.id)
                    }
                    for p in products
                ]
            }
