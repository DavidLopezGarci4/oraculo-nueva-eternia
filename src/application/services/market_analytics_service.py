import copy
from datetime import datetime, timezone, timedelta
import time
from typing import Dict, Any, List, Optional
from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import joinedload

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

_MARKET_INDEX_CACHE_TTL = 300.0  # 5 minutes
# period_key -> (expires_at, base_payload_dict, product_fmv_map)
_market_index_cache: dict[str, tuple[float, Dict[str, Any], Dict[int, float]]] = {}


class MarketAnalyticsService:
    """
    Servicio de Analítica de Mercado y Sincronización Delta.
    Calcula el Índice Bursátil MOTU (Eternia Market Index - EMI) por Waves
    y suministra actualizaciones delta para la caché local en IndexedDB.
    """

    @classmethod
    def invalidate_market_index_cache(cls) -> None:
        _market_index_cache.clear()

    @staticmethod
    def _compute_portfolio_metrics(db, user_id: int, product_fmv_map: Dict[int, float]) -> Optional[Dict[str, Any]]:
        collection_items = db.query(CollectionItemModel).filter(
            CollectionItemModel.owner_id == user_id,
            CollectionItemModel.acquired == True
        ).all()

        if not collection_items:
            return None

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
                if diff >= val * 0.20:
                    bargains_count += 1
                    total_savings_eur += diff
                elif paid >= val * 1.15:
                    overpaid_count += 1

        net_profit_eur = round(total_current_val - total_invested, 2)
        roi_pct = round((net_profit_eur / max(1.0, total_invested)) * 100, 1) if total_invested > 0 else 0.0
        alpha_pct = round((total_savings_eur / max(1.0, total_current_val)) * 100, 1)

        return {
            "total_items_in_collection": len(collection_items),
            "total_invested_eur": round(total_invested, 2),
            "total_market_value_eur": round(total_current_val, 2),
            "net_unrealized_profit_eur": net_profit_eur,
            "roi_percentage": roi_pct,
            "bargains_detected_count": bargains_count,
            "overpaid_count": overpaid_count,
            "total_bargain_savings_eur": round(total_savings_eur, 2),
            "alpha_percentage": alpha_pct,
        }

    @classmethod
    def get_market_index(cls, period: str = "3M", user_id: int = 2, db_session=None) -> Dict[str, Any]:
        """
        Calcula el Índice Bursátil MOTU (EMI) bajo estándar financiero cuantitativo:
        - Horizonte dinámico (1M, 3M, 6M, 1A, ALL) con ventana y half-life EMA adaptados al periodo.
        - Filtrado estadístico de valores atípicos (IQR Interquartile Range).
        - Fair Market Value (FMV) por figura priorizando ofertas activas y reutilizando ProductMonthlyStatsModel.
        - Serie temporal de cesta (Carry-Forward / Interpolación Lineal por Anclas Reales) sin ondas sintéticas.
        """
        import math
        from contextlib import nullcontext

        now = datetime.now(timezone.utc)
        period_key = (period or "3M").upper()
        period_cfg = {
            "1M": {"days": 30, "num_points": 30, "half_life": 10.0},
            "3M": {"days": 90, "num_points": 30, "half_life": 21.0},
            "6M": {"days": 180, "num_points": 30, "half_life": 45.0},
            "1A": {"days": 365, "num_points": 32, "half_life": 90.0},
            "ALL": {"days": 730, "num_points": 35, "half_life": 120.0},
        }
        cfg = period_cfg.get(period_key, period_cfg["3M"])
        days = cfg["days"]
        half_life_days = cfg["half_life"]
        decay_constant = math.log(2) / half_life_days
        available_periods = ["1M", "3M", "6M", "1A", "ALL"]

        use_cache = db_session is None
        mono_now = time.monotonic()

        ctx = nullcontext(db_session) if db_session is not None else SessionCloud()
        with ctx as db:
            if use_cache:
                cached_entry = _market_index_cache.get(period_key)
                if cached_entry is not None and cached_entry[0] > mono_now:
                    base_payload = copy.deepcopy(cached_entry[1])
                    fmv_map = cached_entry[2]
                    base_payload["portfolio_metrics"] = cls._compute_portfolio_metrics(db, user_id, fmv_map)
                    return base_payload

            # 1. Obtener todos los productos modernos de Origins y Crossovers
            products = db.query(ProductModel).filter(
                ProductModel.is_vintage == False
            ).all()

            if not products:
                return {
                    "current_index_value": 28.50,
                    "base_msrp_value": 22.00,
                    "trend_pct": 0.0,
                    "period_change_eur": 0.0,
                    "period_high": 28.50,
                    "period_low": 28.50,
                    "data_span_days": 0,
                    "available_periods": available_periods,
                    "trend_direction": "stable",
                    "status_label": "Mercado Estable",
                    "period": period_key,
                    "historical_series": [],
                    "waves_breakdown": [],
                    "portfolio_metrics": None
                }

            product_ids = {p.id for p in products}

            # 2. Pre-cargar ofertas modernas (filtrando en SQL por ProductModel.is_vintage == False para preservar OfferModel.is_vintage IS NULL)
            try:
                offers = (
                    db.query(OfferModel)
                    .join(ProductModel, OfferModel.product_id == ProductModel.id)
                    .filter(ProductModel.is_vintage == False, OfferModel.price > 0)
                    .all()
                )
            except Exception:
                offers = db.query(OfferModel).filter(OfferModel.price > 0).all()

            prod_offers: Dict[int, List[OfferModel]] = {}
            earliest_real_dt = None

            for o in offers:
                pid = getattr(o, "product_id", None)
                if pid in product_ids:
                    prod_offers.setdefault(pid, []).append(o)
                    for dt_cand in (o.first_seen_at, o.last_seen):
                        if dt_cand is not None:
                            dt_utc = dt_cand if dt_cand.tzinfo else dt_cand.replace(tzinfo=timezone.utc)
                            if earliest_real_dt is None or dt_utc < earliest_real_dt:
                                earliest_real_dt = dt_utc

            try:
                monthly_rows = (
                    db.query(ProductMonthlyStatsModel)
                    .join(ProductModel, ProductMonthlyStatsModel.product_id == ProductModel.id)
                    .filter(
                        ProductModel.is_vintage == False,
                        ProductMonthlyStatsModel.avg_price > 4.0,
                        ProductMonthlyStatsModel.avg_price < 400.0,
                    )
                    .order_by(ProductMonthlyStatsModel.year.asc(), ProductMonthlyStatsModel.month.asc())
                    .all()
                )
            except Exception:
                monthly_rows = (
                    db.query(ProductMonthlyStatsModel)
                    .filter(
                        ProductMonthlyStatsModel.avg_price > 4.0,
                        ProductMonthlyStatsModel.avg_price < 400.0,
                    )
                    .order_by(ProductMonthlyStatsModel.year.asc(), ProductMonthlyStatsModel.month.asc())
                    .all()
                )

            # Mapa mensual por producto: pid -> {(year, month): (price_est, offers_count)}
            prod_monthly_map: Dict[int, Dict[tuple, tuple]] = {}
            latest_monthly_fallback: Dict[int, float] = {}
            for mr in monthly_rows:
                pid = mr.product_id
                if pid not in product_ids or not mr.year or not mr.month:
                    continue
                ym_key = (int(mr.year), int(mr.month))
                rep_price = float(mr.median_price or mr.avg_price or 0.0)
                if rep_price <= 0:
                    continue
                cnt = max(1, int(mr.offers_count or 1))
                m_dt = datetime(ym_key[0], ym_key[1], 1, tzinfo=timezone.utc)
                if earliest_real_dt is None or m_dt < earliest_real_dt:
                    earliest_real_dt = m_dt

                p_map = prod_monthly_map.setdefault(pid, {})
                if ym_key in p_map:
                    prev_p, prev_c = p_map[ym_key]
                    total_c = prev_c + cnt
                    p_map[ym_key] = ((prev_p * prev_c + rep_price * cnt) / total_c, total_c)
                else:
                    p_map[ym_key] = (rep_price, cnt)
                latest_monthly_fallback[pid] = p_map[ym_key][0]

            # Cargar historial granular por producto (filtrado en SQL por ProductModel.is_vintage == False)
            try:
                raw_history = (
                    db.query(
                        OfferModel.product_id,
                        PriceHistoryModel.price,
                        PriceHistoryModel.recorded_at,
                    )
                    .join(OfferModel, PriceHistoryModel.offer_id == OfferModel.id)
                    .join(ProductModel, OfferModel.product_id == ProductModel.id)
                    .filter(
                        ProductModel.is_vintage == False,
                        PriceHistoryModel.price > 4.0,
                        PriceHistoryModel.price < 400.0,
                    )
                    .order_by(PriceHistoryModel.recorded_at.asc())
                    .all()
                )
            except Exception:
                raw_history = (
                    db.query(
                        OfferModel.product_id,
                        PriceHistoryModel.price,
                        PriceHistoryModel.recorded_at,
                    )
                    .join(OfferModel, PriceHistoryModel.offer_id == OfferModel.id)
                    .filter(
                        PriceHistoryModel.price > 4.0,
                        PriceHistoryModel.price < 400.0,
                    )
                    .order_by(PriceHistoryModel.recorded_at.asc())
                    .all()
                )

            prod_daily_map: Dict[int, Dict[str, List[float]]] = {}
            for pid, price_val, rec_at in raw_history:
                if pid not in product_ids or not rec_at:
                    continue
                rec_utc = rec_at if rec_at.tzinfo else rec_at.replace(tzinfo=timezone.utc)
                if earliest_real_dt is None or rec_utc < earliest_real_dt:
                    earliest_real_dt = rec_utc
                d_key = rec_utc.strftime("%Y-%m-%d")
                prod_daily_map.setdefault(pid, {}).setdefault(d_key, []).append(float(price_val))

            # 3. Calcular Fair Market Value (FMV) adaptado al half_life del periodo
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
                        "revaluation_pct": 0.0,
                        "period_change_pct": 0.0,
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
                        avail_boost = 1.25 if getattr(o, "is_available", True) else 0.75
                        w = math.exp(-decay_constant * diff_days) * avail_boost
                        prices.append(float(o.price))
                        weights.append(w)

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
                elif p.id in latest_monthly_fallback:
                    fmv = latest_monthly_fallback[p.id]
                else:
                    fmv = float(p.p25_price) if (p.p25_price and p.p25_price > 0) else (float(p.avg_market_price) if (p.avg_market_price and p.avg_market_price > 0) else msrp)

                product_fmv_map[p.id] = round(fmv, 2)
                waves_breakdown[wave_key]["figures_count"] += 1
                waves_breakdown[wave_key]["avg_msrp"] += msrp
                waves_breakdown[wave_key]["avg_market"] += fmv

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

            # 4. Construir Anclas Reales por Producto (Mensual Compactado >6M + Diario Granular <=6M)
            import statistics as py_stats

            prod_anchors: Dict[int, List[tuple]] = {}
            for p in products:
                pid = p.id
                anchors_dict: Dict[str, tuple] = {}

                # A) Anclas granulares diarias de PriceHistoryModel
                daily_entries = prod_daily_map.get(pid, {})
                granular_months = set()
                for d_str, p_list in daily_entries.items():
                    dt_obj = datetime.strptime(d_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    granular_months.add((dt_obj.year, dt_obj.month))
                    med_p = float(py_stats.median(p_list))
                    anchors_dict[d_str] = (dt_obj, med_p, len(p_list))

                # B) Anclas mensuales compactadas de ProductMonthlyStatsModel para meses sin detalle granular
                for (yr, mo), (m_price, m_cnt) in prod_monthly_map.get(pid, {}).items():
                    if (yr, mo) not in granular_months:
                        m_dt = datetime(yr, mo, 15, tzinfo=timezone.utc)
                        d_str = m_dt.strftime("%Y-%m-%d")
                        anchors_dict[d_str] = (m_dt, float(m_price), int(m_cnt))

                sorted_anc = sorted(anchors_dict.values(), key=lambda x: x[0])
                # Asegurar ancla final en `now` con el FMV actual
                fmv_now = product_fmv_map[pid]
                if not sorted_anc:
                    sorted_anc.append((now, fmv_now, 1))
                elif (now - sorted_anc[-1][0]).total_seconds() > 3600:
                    sorted_anc.append((now, fmv_now, 1))
                else:
                    sorted_anc[-1] = (now, fmv_now, sorted_anc[-1][2])

                prod_anchors[pid] = sorted_anc

            def eval_product_at(pid: int, target_dt: datetime) -> float:
                anc = prod_anchors.get(pid, [])
                if not anc:
                    return product_fmv_map.get(pid, base_msrp)
                if target_dt <= anc[0][0]:
                    return anc[0][1]
                if target_dt >= anc[-1][0]:
                    return anc[-1][1]
                for idx in range(len(anc) - 1):
                    t0, v0, _ = anc[idx]
                    t1, v1, _ = anc[idx + 1]
                    if t0 <= target_dt <= t1:
                        span = (t1 - t0).total_seconds()
                        if span <= 0:
                            return v1
                        ratio = (target_dt - t0).total_seconds() / span
                        return v0 + ratio * (v1 - v0)
                return anc[-1][1]

            # Determinar el inicio efectivo de la ventana temporal sin inventar datos previos al origen real
            requested_start = now - timedelta(days=days)
            if earliest_real_dt is not None:
                if period_key == "ALL":
                    effective_start = min(earliest_real_dt, now - timedelta(days=7))
                else:
                    effective_start = max(requested_start, min(earliest_real_dt, now - timedelta(days=7)))
            else:
                effective_start = requested_start

            span_seconds = max(86400.0, (now - effective_start).total_seconds())
            effective_days = max(1, int(round(span_seconds / 86400.0)))
            num_points = min(max(7, effective_days), cfg["num_points"])
            step_seconds = span_seconds / max(1, num_points)

            historical_series = []
            for i in range(num_points + 1):
                pt_dt = effective_start + timedelta(seconds=i * step_seconds)
                if i == num_points:
                    pt_dt = now
                d_str = pt_dt.strftime("%Y-%m-%d")
                ym_key = (pt_dt.year, pt_dt.month)

                basket_vals = [eval_product_at(p.id, pt_dt) for p in products]
                idx_val = round(sum(basket_vals) / max(1, len(basket_vals)), 2)

                # Volumen observado en torno al bucket
                vol = 0
                for p in products:
                    if d_str in prod_daily_map.get(p.id, {}):
                        vol += len(prod_daily_map[p.id][d_str])
                    elif ym_key in prod_monthly_map.get(p.id, {}):
                        vol += prod_monthly_map[p.id][ym_key][1]
                if vol == 0:
                    vol = len(prod_offers)

                historical_series.append({
                    "date": d_str,
                    "index_value": idx_val,
                    "volume": vol
                })

            if historical_series:
                historical_series[-1]["index_value"] = current_index
                historical_series[-1]["date"] = now.strftime("%Y-%m-%d")

            # Calcular variación por subcategoría dentro del periodo seleccionado
            for p in products:
                wave_key = (p.sub_category or "Origins").strip()
                waves_breakdown[wave_key].setdefault("_start_sum", 0.0)
                waves_breakdown[wave_key]["_start_sum"] += eval_product_at(p.id, effective_start)

            for k, v in waves_breakdown.items():
                cnt = max(1, v["figures_count"])
                start_wave_avg = v.pop("_start_sum", v["avg_market"] * cnt) / cnt
                if start_wave_avg > 0:
                    v["period_change_pct"] = round(((v["avg_market"] - start_wave_avg) / start_wave_avg) * 100, 1)

            series_vals = [pt["index_value"] for pt in historical_series] if historical_series else [current_index]
            start_index = series_vals[0]
            period_high = round(max(series_vals), 2)
            period_low = round(min(series_vals), 2)
            period_change_eur = round(current_index - start_index, 2)
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

            sorted_waves = sorted(list(waves_breakdown.values()), key=lambda w: w["revaluation_pct"], reverse=True)

            base_payload = {
                "current_index_value": current_index,
                "base_msrp_value": base_msrp,
                "trend_pct": trend_pct,
                "period_change_eur": period_change_eur,
                "period_high": period_high,
                "period_low": period_low,
                "data_span_days": effective_days,
                "available_periods": available_periods,
                "trend_direction": direction,
                "status_label": status_label,
                "period": period_key,
                "historical_series": historical_series,
                "waves_breakdown": sorted_waves,
                "portfolio_metrics": None,
            }

            if use_cache:
                _market_index_cache[period_key] = (
                    mono_now + _MARKET_INDEX_CACHE_TTL,
                    copy.deepcopy(base_payload),
                    dict(product_fmv_map),
                )

            base_payload["portfolio_metrics"] = cls._compute_portfolio_metrics(db, user_id, product_fmv_map)
            return base_payload

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
            offers = (
                db.query(OfferModel)
                .options(joinedload(OfferModel.product))
                .filter(
                    OfferModel.is_available == True,
                    OfferModel.is_vintage.is_not(True),
                    OfferModel.price > 0,
                )
                .all()
            )

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
        rules_map = LogisticsService.get_cached_rules_map()
        with SessionCloud() as db:
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
                    query = query.filter(ProductModel.updated_at >= dt)
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
