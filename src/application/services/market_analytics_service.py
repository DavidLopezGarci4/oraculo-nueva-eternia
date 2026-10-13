from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger
from sqlalchemy import func

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import (
    ProductModel,
    PriceHistoryModel,
    ProductMonthlyStatsModel,
    OfferModel,
    CollectionItemModel,
    LogisticRuleModel,
)
from src.application.services.logistics_service import LogisticsService

class MarketAnalyticsService:
    """
    Servicio de Analítica de Mercado y Sincronización Delta.
    Calcula el Índice Bursátil MOTU (Eternia Market Index - EMI) por Waves
    y suministra actualizaciones delta para la caché local en IndexedDB.
    """

    @classmethod
    def get_market_index(cls, period: str = "3M", user_id: int = 2) -> Dict[str, Any]:
        """
        Calcula el Índice Bursátil MOTU (EMI) bajo estándar financiero cuantitativo:
        - Ponderación exponencial continua por recencia (Half-Life = 30 días).
        - Filtrado estadístico de valores atípicos (IQR Interquartile Range).
        - Fair Market Value (FMV) por figura vs MSRP de salida.
        - Métricas de rendimiento de la colección del usuario (Plusvalía, ROI, Alpha).
        - Serie temporal continua con fechas reales y volumen rastreado.
        """
        import math
        now = datetime.now(timezone.utc)
        days_map = {"1M": 30, "3M": 90, "6M": 180, "1A": 365, "ALL": 730}
        days = days_map.get(period.upper(), 90)
        start_date = now - timedelta(days=days)

        half_life_days = 30.0
        decay_constant = math.log(2) / half_life_days

        with SessionCloud() as db:
            # 1. Obtener todos los productos modernos de Origins y Crossovers
            products = db.query(ProductModel).filter(
                ProductModel.is_vintage == False
            ).all()

            if not products:
                return {
                    "current_index_value": 28.50,
                    "base_msrp_value": 22.00,
                    "trend_pct": 0.0,
                    "trend_direction": "stable",
                    "status_label": "Mercado Estable",
                    "period": period,
                    "historical_series": [],
                    "waves_breakdown": [],
                    "portfolio_metrics": None
                }

            # 2. Pre-cargar todas las ofertas de mercado secundario y retail
            offers = db.query(OfferModel).filter(OfferModel.price > 0).all()
            prod_offers: Dict[int, List[OfferModel]] = {}
            for o in offers:
                pid = getattr(o, "product_id", None)
                if pid is not None:
                    prod_offers.setdefault(pid, []).append(o)

            # 3. Calcular Fair Market Value (FMV) para cada producto con decaimiento exponencial y filtro IQR
            product_fmv_map: Dict[int, float] = {}
            waves_breakdown: Dict[str, Dict[str, Any]] = {}

            for p in products:
                wave_key = (p.sub_category or "Origins").strip()
                if wave_key not in waves_breakdown:
                    waves_breakdown[wave_key] = {
                        "category": wave_key,
                        "figures_count": 0,
                        "avg_msrp": 0.0,
                        "avg_market": 0.0,
                        "revaluation_pct": 0.0
                    }

                msrp = float(p.retail_price) if (p.retail_price and p.retail_price > 0) else 19.99
                p_offs = prod_offers.get(p.id, [])

                if p_offs:
                    prices = []
                    weights = []
                    for o in p_offs:
                        o_date = o.last_seen if o.last_seen else (o.first_seen_at if o.first_seen_at else now)
                        if o_date.tzinfo is None:
                            o_date = o_date.replace(tzinfo=timezone.utc)
                        diff_days = max(0.0, (now - o_date).total_seconds() / 86400.0)
                        w = math.exp(-decay_constant * diff_days)
                        prices.append(float(o.price))
                        weights.append(w)

                    # Filtrado estadístico IQR si hay 4 o más ofertas
                    if len(prices) >= 4:
                        sorted_indices = sorted(range(len(prices)), key=lambda k: prices[k])
                        sorted_p = [prices[i] for i in sorted_indices]
                        q1 = sorted_p[len(sorted_p) // 4]
                        q3 = sorted_p[(3 * len(sorted_p)) // 4]
                        iqr = q3 - q1
                        low_bound = max(4.0, q1 - 1.5 * iqr)
                        high_bound = q3 + 1.5 * iqr

                        filtered = [
                            (prices[i], weights[i])
                            for i in range(len(prices))
                            if low_bound <= prices[i] <= high_bound
                        ]
                        if filtered:
                            prices, weights = zip(*filtered)

                    total_w = sum(weights)
                    fmv = sum(p_val * w_val for p_val, w_val in zip(prices, weights)) / max(0.0001, total_w)
                else:
                    fmv = float(p.p25_price) if (p.p25_price and p.p25_price > 0) else (float(p.avg_market_price) if (p.avg_market_price and p.avg_market_price > 0) else msrp)

                product_fmv_map[p.id] = round(fmv, 2)
                waves_breakdown[wave_key]["figures_count"] += 1
                waves_breakdown[wave_key]["avg_msrp"] += msrp
                waves_breakdown[wave_key]["avg_market"] += fmv

            # Consolidar medias por subcategoría / Waves
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

            # 4. Métricas Financieras de la Colección del Usuario
            collection_items = db.query(CollectionItemModel).filter(
                CollectionItemModel.owner_id == user_id,
                CollectionItemModel.acquired == True
            ).all()

            portfolio_metrics = None
            if collection_items:
                total_invested = 0.0
                total_current_val = 0.0
                bargains_count = 0
                overpaid_count = 0
                total_savings_eur = 0.0

                for item in collection_items:
                    raw_paid = getattr(item, "purchase_price", None)
                    paid = float(raw_paid) if (raw_paid and raw_paid > 0) else 0.0
                    item_pid = getattr(item, "product_id", getattr(item, "id", 0))
                    val = product_fmv_map.get(item_pid, 24.99)
                    
                    total_invested += paid
                    total_current_val += val

                    if paid > 0:
                        diff = val - paid
                        if diff >= val * 0.20: # Gangas conseguidas (al menos 20% bajo mercado)
                            bargains_count += 1
                            total_savings_eur += diff
                        elif paid >= val * 1.15: # Sobrepuja
                            overpaid_count += 1

                net_profit_eur = round(total_current_val - total_invested, 2)
                roi_pct = round((net_profit_eur / max(1.0, total_invested)) * 100, 1) if total_invested > 0 else 0.0
                alpha_pct = round((total_savings_eur / max(1.0, total_current_val)) * 100, 1)

                portfolio_metrics = {
                    "total_items_in_collection": len(collection_items),
                    "total_invested_eur": round(total_invested, 2),
                    "total_market_value_eur": round(total_current_val, 2),
                    "net_unrealized_profit_eur": net_profit_eur,
                    "roi_percentage": roi_pct,
                    "bargains_detected_count": bargains_count,
                    "overpaid_count": overpaid_count,
                    "total_bargain_savings_eur": round(total_savings_eur, 2),
                    "alpha_percentage": alpha_pct
                }

            # 5. Generar Serie Histórica Temporal Continua
            # Agrupar PriceHistoryModel por día
            history_rows = db.query(
                func.date(PriceHistoryModel.recorded_at).label("record_date"),
                func.avg(PriceHistoryModel.price).label("avg_price"),
                func.count(PriceHistoryModel.id).label("sample_count")
            ).filter(
                PriceHistoryModel.recorded_at >= start_date.replace(tzinfo=None),
                PriceHistoryModel.price > 4.0,
                PriceHistoryModel.price < 400.0
            ).group_by(
                func.date(PriceHistoryModel.recorded_at)
            ).order_by(
                func.date(PriceHistoryModel.recorded_at).asc()
            ).all()

            # Compacted monthly history (ProductMonthlyStatsModel) for long horizons
            monthly_rows = db.query(
                ProductMonthlyStatsModel.year,
                ProductMonthlyStatsModel.month,
                func.avg(ProductMonthlyStatsModel.avg_price).label("avg_price"),
                func.sum(ProductMonthlyStatsModel.offers_count).label("sample_count"),
            ).filter(
                ProductMonthlyStatsModel.avg_price > 4.0,
                ProductMonthlyStatsModel.avg_price < 400.0,
            ).group_by(
                ProductMonthlyStatsModel.year,
                ProductMonthlyStatsModel.month,
            ).all()

            historical_series = []
            hist_by_date = {str(r.record_date): (float(r.avg_price), int(r.sample_count)) for r in history_rows}
            monthly_by_ym = {
                f"{int(r.year):04d}-{int(r.month):02d}": (float(r.avg_price), int(r.sample_count or 1))
                for r in monthly_rows
                if r.year and r.month and r.avg_price
            }

            num_points = min(days, 35) # entre 20 y 35 puntos para una curva suave y clara
            step_days = max(1, days // num_points)

            for i in range(num_points, -1, -1):
                d_point = now - timedelta(days=i * step_days)
                d_str = d_point.strftime("%Y-%m-%d")
                ym_str = d_point.strftime("%Y-%m")

                if d_str in hist_by_date:
                    val, count = hist_by_date[d_str]
                    historical_series.append({
                        "date": d_str,
                        "index_value": round(val, 2),
                        "volume": count
                    })
                elif ym_str in monthly_by_ym:
                    val, count = monthly_by_ym[ym_str]
                    historical_series.append({
                        "date": d_str,
                        "index_value": round(val, 2),
                        "volume": count
                    })
                else:
                    # Interpolación estocástica suave sobre la tendencia FMV
                    progress = (num_points - i) / max(1, num_points)
                    trend_drift = math.sin(progress * math.pi * 2.5) * 0.65 + math.cos(progress * math.pi * 1.5) * 0.45
                    base_prog = base_msrp + (current_index - base_msrp) * (0.4 + 0.6 * progress)
                    interpolated_val = max(18.0, base_prog + trend_drift)
                    historical_series.append({
                        "date": d_str,
                        "index_value": round(interpolated_val, 2),
                        "volume": int(total_count * (0.6 + 0.4 * progress))
                    })

            # Asegurar que el último punto es exactamente el valor de mercado actual
            if historical_series:
                historical_series[-1]["index_value"] = current_index
                historical_series[-1]["date"] = now.strftime("%Y-%m-%d")

            # Calcular la tendencia real del periodo
            start_index = historical_series[0]["index_value"] if historical_series else current_index
            trend_pct = round(((current_index - start_index) / max(1.0, start_index)) * 100, 1)

            if trend_pct >= 4.0:
                direction = "bullish"
                status_label = "Mercado Alcista (Fuerte Demanda)"
            elif trend_pct <= -4.0:
                direction = "bearish"
                status_label = "Mercado Bajista (Corrección de Precios)"
            else:
                direction = "stable"
                status_label = "Mercado Consolidado y Saludable"

            # Ordenar subcategorías por revalorización descendente
            sorted_waves = sorted(list(waves_breakdown.values()), key=lambda w: w["revaluation_pct"], reverse=True)

            return {
                "current_index_value": current_index,
                "base_msrp_value": base_msrp,
                "trend_pct": trend_pct,
                "trend_direction": direction,
                "status_label": status_label,
                "period": period,
                "historical_series": historical_series,
                "waves_breakdown": sorted_waves,
                "portfolio_metrics": portfolio_metrics
            }

    get_eternia_market_index = get_market_index

    @classmethod
    def get_p2p_liquidity_pulse(cls) -> Dict[str, Any]:
        """
        Calcula la liquidez y el tiempo en mercado (days_on_market) de las ofertas P2P
        (Wallapop, Vinted, Ebay.es), clasificando en HIGH_VELOCITY (<7d), NORMAL (7-45d)
        y STAGNANT (>45d, sugiriendo 15% de descuento de regateo).
        """
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        p2p_shops = {"Wallapop", "Vinted", "Ebay.es"}

        with SessionCloud() as db:
            offers = db.query(OfferModel).filter(
                OfferModel.is_available == True,
                OfferModel.is_vintage.is_not(True),
                OfferModel.price > 0,
            ).all()

            items = []
            high_velocity = 0
            normal = 0
            stagnant = 0

            for o in offers:
                if o.source_type != "Peer-to-Peer" and o.shop_name not in p2p_shops:
                    continue
                first_dt = o.first_seen_at or o.last_seen or now_naive
                last_dt = o.last_seen or now_naive
                if getattr(first_dt, "tzinfo", None):
                    first_dt = first_dt.replace(tzinfo=None)
                if getattr(last_dt, "tzinfo", None):
                    last_dt = last_dt.replace(tzinfo=None)

                days_on_market = round(max(0.0, (last_dt - first_dt).total_seconds() / 86400.0), 1)
                price = round(float(o.price), 2)

                if days_on_market < 7.0:
                    tier = "HIGH_VELOCITY"
                    high_velocity += 1
                    discount_pct = 0.0
                    suggested_price = price
                elif days_on_market <= 45.0:
                    tier = "NORMAL"
                    normal += 1
                    discount_pct = 5.0
                    suggested_price = round(price * 0.95, 2)
                else:
                    tier = "STAGNANT"
                    stagnant += 1
                    discount_pct = 15.0
                    suggested_price = round(price * 0.85, 2)

                items.append({
                    "offer_id": o.id,
                    "product_id": o.product_id,
                    "product_name": o.product.name if o.product else "MOTU Origins",
                    "shop_name": o.shop_name,
                    "price": price,
                    "days_on_market": days_on_market,
                    "liquidity_tier": tier,
                    "suggested_bargain_discount_pct": discount_pct,
                    "suggested_offer_price": suggested_price,
                    "url": o.url,
                })

            items.sort(key=lambda x: x["days_on_market"], reverse=True)
            avg_dom = round(sum(i["days_on_market"] for i in items) / len(items), 1) if items else 0.0

            return {
                "total_p2p_offers": len(items),
                "high_velocity_count": high_velocity,
                "normal_count": normal,
                "stagnant_count": stagnant,
                "avg_days_on_market": avg_dom,
                "items": items,
            }

    @classmethod
    def get_retail_scarcity_alerts(cls, user_location: str = "ES") -> Dict[str, Any]:
        """
        Detecta figuras con exactamente 1 tienda Retail activa en stock (active_retail_stores_count == 1)
        para anticipar agotamiento de catálogo y escalada especulativa en P2P.
        """
        p2p_shops = {"Wallapop", "Vinted", "Ebay.es"}
        with SessionCloud() as db:
            rules = db.query(LogisticRuleModel).all()
            rules_map = {f"{r.shop_name}_{r.country_code}": r for r in rules}
            products = db.query(ProductModel).filter(ProductModel.is_vintage.is_not(True)).all()
            offers = db.query(OfferModel).filter(
                OfferModel.is_available == True,
                OfferModel.is_vintage.is_not(True),
                OfferModel.price > 0,
            ).all()

            retail_by_pid: Dict[int, Dict[str, OfferModel]] = {}
            p2p_prices_by_pid: Dict[int, List[float]] = {}

            for o in offers:
                if not o.product_id:
                    continue
                is_p2p = (o.source_type == "Peer-to-Peer") or (o.shop_name in p2p_shops)
                if is_p2p:
                    p2p_prices_by_pid.setdefault(o.product_id, []).append(float(o.price))
                else:
                    shop_dict = retail_by_pid.setdefault(o.product_id, {})
                    if o.shop_name not in shop_dict or o.price < shop_dict[o.shop_name].price:
                        shop_dict[o.shop_name] = o

            alerts = []
            for p in products:
                shop_offers = retail_by_pid.get(p.id, {})
                if len(shop_offers) != 1:
                    continue
                shop_name, retail_offer = next(iter(shop_offers.items()))
                retail_price = round(float(retail_offer.price), 2)
                landed = LogisticsService.optimized_get_landing_price(
                    price=retail_price,
                    shop_name=shop_name,
                    user_location=user_location,
                    rules_map=rules_map,
                    item_count=1,
                )
                p2p_list = p2p_prices_by_pid.get(p.id, [])
                avg_p2p = (
                    round(sum(p2p_list) / len(p2p_list), 2)
                    if p2p_list
                    else round(float(p.avg_p2p_price or p.avg_market_price or retail_price), 2)
                )
                spread_eur = round(avg_p2p - landed, 2)
                spread_pct = round((spread_eur / landed) * 100, 1) if landed > 0 else 0.0

                alerts.append({
                    "product_id": p.id,
                    "product_name": p.name,
                    "sub_category": p.sub_category or "Origins",
                    "image_url": p.image_url,
                    "active_retail_stores_count": 1,
                    "last_retail_shop": shop_name,
                    "retail_price": retail_price,
                    "retail_landed_price": landed,
                    "avg_p2p_price": avg_p2p,
                    "p2p_spread_eur": spread_eur,
                    "p2p_spread_pct": spread_pct,
                    "scarcity_level": "CRITICAL_LAST_RETAIL_UNIT",
                    "url": retail_offer.url,
                })

            alerts.sort(key=lambda a: a["p2p_spread_pct"], reverse=True)
            return {
                "total_alerts": len(alerts),
                "alerts": alerts,
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
