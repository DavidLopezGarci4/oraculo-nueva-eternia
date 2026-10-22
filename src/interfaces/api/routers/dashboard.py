import json
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import contains_eager

from src.application.services.logistics_service import LogisticsService
from src.domain.models import (
    BlackcludedItemModel,
    CollectionItemModel,
    LogisticRuleModel,
    OfferHistoryModel,
    OfferModel,
    PendingMatchModel,
    ProductModel,
    UserModel,
)
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_api_key, verify_device
from src.interfaces.api.schemas import (
    DashboardStatsOutput,
    HallOfFameOutput,
    TopDealOutput,
    MatchStatOutput,
    MatchHistoryOutput,
    StatusMessageOutput,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsOutput, dependencies=[Depends(verify_device)])
def get_dashboard_stats(user_id: int = 1):
    try:
        with SessionCloud() as db:
            # Query 1: User location
            user_location = "ES"
            user_row = db.query(UserModel.location).filter(UserModel.id == user_id).first()
            if user_row and user_row[0]:
                user_location = user_row[0]

            # Query 2: Lightweight projection of all products for counts and wave completion
            all_products = db.query(
                ProductModel.id,
                ProductModel.name,
                ProductModel.sub_category,
                ProductModel.is_vintage,
            ).all()

            total_products = 0
            total_products_vintage = 0
            for _pid, _pname, _sub, is_v in all_products:
                if is_v:
                    total_products_vintage += 1
                else:
                    total_products += 1

            # Query 3: All collection items for user (owned & wish, modern & vintage) with eager ProductModel
            all_coll_items = (
                db.query(CollectionItemModel)
                .join(ProductModel)
                .options(contains_eager(CollectionItemModel.product))
                .filter(CollectionItemModel.owner_id == user_id)
                .all()
            )

            owned_count = 0
            owned_count_vintage = 0
            wish_count = 0
            wish_count_vintage = 0
            acquired_items: list[CollectionItemModel] = []
            owned_product_ids: set[int] = set()

            for ci in all_coll_items:
                is_v = bool(ci.product.is_vintage) if ci.product else False
                if ci.acquired:
                    acquired_items.append(ci)
                    if ci.product_id:
                        owned_product_ids.add(ci.product_id)
                    if is_v:
                        owned_count_vintage += 1
                    else:
                        owned_count += 1
                else:
                    if is_v:
                        wish_count_vintage += 1
                    else:
                        wish_count += 1

            # Query 4: Preload active offers once for all acquired items (modern + vintage)
            from src.application.services.valuation_service import ValuationService

            valuation_service = ValuationService(db)
            valuation_service.preload_offers_for_products(list(owned_product_ids))

            total_invested = 0.0
            market_value = 0.0
            total_invested_v = 0.0
            market_value_v = 0.0

            condition_buckets = {
                "MOC": {"count": 0, "value": 0.0},
                "Loose": {"count": 0, "value": 0.0},
                "New": {"count": 0, "value": 0.0},
            }

            for item in acquired_items:
                if not item.product:
                    continue
                base_val, _ = valuation_service.get_product_valuation_pair(
                    item.product, user_location
                )
                mult = valuation_service.get_condition_multiplier(
                    item.condition, item.grading
                )
                adjusted_val = base_val * mult
                invested = item.purchase_price or 0.0

                if item.product.is_vintage:
                    market_value_v += adjusted_val
                    total_invested_v += invested
                else:
                    market_value += adjusted_val
                    total_invested += invested

                raw_cond = (item.condition or "MOC").strip().upper()
                if raw_cond == "NEW":
                    cond_key = "New"
                elif raw_cond == "LOOSE":
                    cond_key = "Loose"
                else:
                    cond_key = "MOC"

                condition_buckets[cond_key]["count"] += 1
                condition_buckets[cond_key]["value"] += adjusted_val

            profit_loss = market_value - total_invested
            roi = (profit_loss / total_invested * 100) if total_invested > 0 else 0.0

            profit_loss_v = market_value_v - total_invested_v
            roi_v = (profit_loss_v / total_invested_v * 100) if total_invested_v > 0 else 0.0

            condition_breakdown = [
                {
                    "name": k,
                    "value": int(v["count"]),
                    "estimatedValue": round(float(v["value"]), 2),
                }
                for k, v in condition_buckets.items()
                if v["count"] > 0
            ]

            waves_map: dict[str, dict] = {}
            for pid, pname, sub_cat, is_v in all_products:
                sub = sub_cat or "Otros"
                entry = waves_map.get(sub)
                if entry is None:
                    entry = {
                        "total": 0,
                        "owned": 0,
                        "missing_names": [],
                        "missing_count": 0,
                        "isVintage": bool(is_v),
                    }
                    waves_map[sub] = entry
                entry["total"] += 1
                if pid in owned_product_ids:
                    entry["owned"] += 1
                else:
                    entry["missing_count"] += 1
                    if len(entry["missing_names"]) < 3:
                        entry["missing_names"].append(pname)
                if is_v:
                    entry["isVintage"] = True

            waves_completion = sorted(
                [
                    {
                        "name": name,
                        "total": data["total"],
                        "owned": data["owned"],
                        "percentage": round(
                            (data["owned"] / data["total"]) * 100, 1
                        )
                        if data["total"] > 0
                        else 0.0,
                        "missing_names": data["missing_names"],
                        "missing_count": data["missing_count"],
                        "isVintage": data["isVintage"],
                    }
                    for name, data in waves_map.items()
                    if data["total"] > 0
                ],
                key=lambda w: w["percentage"],
                reverse=True,
            )

            # Query 5: Shop distribution
            shop_dist = (
                db.query(OfferModel.shop_name, func.count(OfferModel.id))
                .filter(
                    OfferModel.product_id.isnot(None),
                    OfferModel.is_available == True,
                    OfferModel.source_type == "Retail",
                )
                .group_by(OfferModel.shop_name)
                .all()
            )

            match_count = sum(count for _, count in shop_dist)

            return {
                "total_products": total_products,
                "total_products_vintage": total_products_vintage,
                "owned_count": owned_count,
                "owned_count_vintage": owned_count_vintage,
                "wish_count": wish_count,
                "wish_count_vintage": wish_count_vintage,
                "financial": {
                    "total_invested": round(total_invested, 2),
                    "market_value": round(market_value, 2),
                    "landed_market_value": round(market_value, 2),
                    "profit_loss": round(profit_loss, 2),
                    "roi": round(roi, 1),
                },
                "financial_vintage": {
                    "total_invested": round(total_invested_v, 2),
                    "market_value": round(market_value_v, 2),
                    "landed_market_value": round(market_value_v, 2),
                    "profit_loss": round(profit_loss_v, 2),
                    "roi": round(roi_v, 1),
                },
                "match_count": match_count,
                "shop_distribution": [{"shop": s, "count": c} for s, c in shop_dist],
                "condition_breakdown": condition_breakdown,
                "waves_completion": waves_completion,
            }

    except Exception as e:
        logger.error(f"CRITICAL DASHBOARD ERROR for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al recuperar datos del tablero: {str(e)}")


@router.get("/hall-of-fame", response_model=HallOfFameOutput, dependencies=[Depends(verify_device)])
def get_dashboard_hall_of_fame(user_id: int = 1):
    with SessionCloud() as db:
        items = (
            db.query(CollectionItemModel)
            .join(ProductModel)
            .options(contains_eager(CollectionItemModel.product))
            .filter(CollectionItemModel.acquired == True, CollectionItemModel.owner_id == user_id)
            .all()
        )

        if not items:
            return {
                "origins": {"top_value": [], "top_roi": []},
                "vintage": {"top_value": [], "top_roi": []}
            }

        from src.application.services.valuation_service import ValuationService

        valuation_service = ValuationService(db)
        
        # Pre-cargar ofertas activas para optimizar consultas N+1 en loops
        product_ids = [item.product_id for item in items if item.product_id]
        valuation_service.preload_offers_for_products(product_ids)

        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            user_location = user.location

        origins_items = []
        vintage_items = []

        for item in items:
            market_val = valuation_service.get_consolidated_value(item.product, user_location)
            
            user_paid = item.purchase_price or 0.0
            retail_val = item.product.retail_price or 0.0
            p2p_val = item.product.avg_p2p_price or item.product.avg_market_price or market_val

            # ROI de adquisición (vs lo que pagó el usuario)
            roi_purchase = 0.0
            if user_paid > 0:
                roi_purchase = ((market_val - user_paid) / user_paid) * 100

            # ROI de revalorización histórica (vs PVP de lanzamiento)
            roi_retail = 0.0
            if retail_val > 0:
                roi_retail = ((market_val - retail_val) / retail_val) * 100

            effective_invested = user_paid if user_paid > 0 else (retail_val if retail_val > 0 else market_val)
            effective_roi = roi_purchase if user_paid > 0 else roi_retail

            data = {
                "id": item.product.id,
                "name": item.product.name,
                "image_url": item.product.image_url,
                "figure_id": item.product.figure_id,
                "market_value": round(market_val, 2),
                "purchase_price": round(effective_invested, 2),
                "invested_value": round(effective_invested, 2),  # Compatibilidad frontend
                "retail_price": round(retail_val, 2),
                "p2p_price": round(p2p_val, 2),
                "roi": round(effective_roi, 1),
                "roi_percentage": round(effective_roi, 1),  # Compatibilidad frontend
                "roi_retail": round(roi_retail, 1),
                "category": item.product.category or ("Vintage" if item.product.is_vintage else "Origins"),
                "sub_category": item.product.sub_category or "",
                "condition": item.condition or "MOC",
                "grading": item.grading or 10.0,
                "notes": item.notes or "",
                "acquired_at": item.acquired_at.isoformat() if item.acquired_at else None,
                "is_vintage": bool(item.product.is_vintage),
            }

            if item.product.is_vintage:
                vintage_items.append(data)
            else:
                origins_items.append(data)

        # Segmentar y ordenar
        origins_top_value = sorted(origins_items, key=lambda x: x["market_value"], reverse=True)[:5]
        origins_top_roi = sorted([i for i in origins_items if i["roi"] > 0], key=lambda x: x["roi"], reverse=True)[:5]

        vintage_top_value = sorted(vintage_items, key=lambda x: x["market_value"], reverse=True)[:5]
        vintage_top_roi = sorted([i for i in vintage_items if i["roi"] > 0], key=lambda x: x["roi"], reverse=True)[:5]

        return {
            "origins": {
                "top_value": origins_top_value,
                "top_roi": origins_top_roi,
            },
            "vintage": {
                "top_value": vintage_top_value,
                "top_roi": vintage_top_roi,
            }
        }


@router.get("/top-deals", response_model=List[TopDealOutput], dependencies=[Depends(verify_device)])
def get_top_deals(user_id: int = 2, mode: str = Query("landed", description="'landed' or 'base'")):
    with SessionCloud() as db:
        owned_ids = [
            p[0]
            for p in db.query(CollectionItemModel.product_id).filter(
                CollectionItemModel.owner_id == user_id,
                CollectionItemModel.acquired == True,
            ).all()
        ]

        freshness_threshold = datetime.now(timezone.utc) - timedelta(hours=72)

        # rules_map cached via LogisticsService.get_cached_rules_map(db)
        rules_map = LogisticsService.get_cached_rules_map(db)

        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            user_location = user.location

        # Consultar ofertas candidatas activas sin filtro SQL prematuro de MIN(price)
        query = (
            db.query(OfferModel)
            .join(ProductModel)
            .options(contains_eager(OfferModel.product))
            .filter(
                OfferModel.is_available == True,
                OfferModel.last_seen >= freshness_threshold,
                OfferModel.source_type == "Retail",
                OfferModel.opportunity_score > 0,
            )
        )
        if owned_ids:
            query = query.filter(OfferModel.product_id.notin_(owned_ids))

        all_candidate_offers = query.all()

        # Agrupar por producto y seleccionar la mejor oferta según el modo
        best_by_product = {}
        for o in all_candidate_offers:
            if not o.product:
                continue
            landing_p = LogisticsService.optimized_get_landing_price(o.price, o.shop_name, user_location, rules_map)
            retail = float(o.product.retail_price or 19.99)
            base_p = float(o.price)

            # En modo "base", el cálculo de descuento se basa en el precio puro de tienda sin envío
            # En modo "landed", se basa en el precio puesto en casa
            ref_price = base_p if mode == "base" else landing_p
            discount = max(0.0, round(((retail - ref_price) / retail) * 100, 1)) if retail > 0 else 0.0

            item_data = {
                "id": o.id,
                "product_id": o.product_id,
                "product_name": o.product.name,
                "price": round(base_p, 2),
                "landing_price": round(landing_p, 2),
                "shop_name": o.shop_name,
                "url": o.url,
                "opportunity_score": o.opportunity_score,
                "image_url": o.product.image_url,
                "retail_price": retail,
                "discount_pct": discount,
            }

            if o.product_id not in best_by_product:
                best_by_product[o.product_id] = item_data
            else:
                current_best = best_by_product[o.product_id]
                if mode == "base":
                    # Comparación por precio base de tienda
                    if base_p < current_best["price"] or (
                        abs(base_p - current_best["price"]) < 0.01 and o.opportunity_score > current_best["opportunity_score"]
                    ):
                        best_by_product[o.product_id] = item_data
                else:
                    # Comparación por landed price
                    if landing_p < current_best["landing_price"] or (
                        abs(landing_p - current_best["landing_price"]) < 0.01 and o.opportunity_score > current_best["opportunity_score"]
                    ):
                        best_by_product[o.product_id] = item_data

        deals = list(best_by_product.values())
        if mode == "base":
            deals.sort(key=lambda x: (x["price"], -x["opportunity_score"]))
        else:
            deals.sort(key=lambda x: (x["landing_price"], -x["opportunity_score"]))

        seen_names = set()
        final_deals = []
        for r in deals:
            if r["product_name"] not in seen_names:
                seen_names.add(r["product_name"])
                final_deals.append(r)

        return final_deals[:20]


@router.get("/match-stats", response_model=List[MatchStatOutput], dependencies=[Depends(verify_device)])
def get_dashboard_match_stats():
    with SessionCloud() as db:
        stats = (
            db.query(OfferModel.shop_name.label("shop"), func.count(OfferModel.id).label("count"))
            .filter(OfferModel.product_id.isnot(None), OfferModel.is_available == True)
            .group_by(OfferModel.shop_name)
            .all()
        )

        return [{"shop": s.shop, "count": s.count} for s in stats]


@router.get("/history", response_model=List[MatchHistoryOutput], dependencies=[Depends(verify_device)])
def get_dashboard_history():
    with SessionCloud() as db:
        history = (
            db.query(OfferHistoryModel)
            .order_by(desc(OfferHistoryModel.timestamp))
            .limit(10)
            .all()
        )

        return [
            {
                "id": h.id,
                "product_name": h.product_name,
                "shop_name": h.shop_name,
                "price": h.price,
                "action_type": h.action_type,
                "timestamp": h.timestamp.isoformat(),
                "offer_url": h.offer_url,
            }
            for h in history
        ]


@router.post("/revert", response_model=StatusMessageOutput, dependencies=[Depends(verify_api_key)])
def revert_action(request: dict):
    # Fase AAA-2.1 / Fix Logística: esta acción borra/reconstruye entradas de OfferModel,
    # BlackcludedItemModel, VintageMiscellaneousModel e historial con soporte completo de tipos
    history_id = request.get("history_id")
    if not history_id:
        raise HTTPException(status_code=400, detail="ID de historial requerido")

    from src.core.url_utils import normalize_url
    from src.domain.models import VintageMiscellaneousModel, VintageProductModel, ProductAliasModel

    with SessionCloud() as db:
        history = db.query(OfferHistoryModel).filter(OfferHistoryModel.id == history_id).first()
        if not history:
            raise HTTPException(status_code=404, detail="Entrada de historial no encontrada")

        raw_url = history.offer_url
        norm_url = normalize_url(raw_url) if raw_url else raw_url
        urls_to_match = list(set(filter(None, [raw_url, norm_url])))

        original_item = None
        try:
            if history.details:
                details_json = json.loads(history.details)
                if isinstance(details_json, dict):
                    original_item = details_json.get("original_item")
        except Exception:
            logger.warning(f"Reconstruction Fallback for History ID {history_id}: No JSON metadata found.")

        # 1. Clean up blacklist (BlackcludedItemModel)
        bl_items = db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url.in_(urls_to_match)).all()
        bl_scraped_name = bl_items[0].scraped_name if bl_items and bl_items[0].scraped_name else None
        bl_source_type = bl_items[0].source_type if bl_items and hasattr(bl_items[0], 'source_type') else None
        for bl in bl_items:
            db.delete(bl)

        # 2. Clean up offers (OfferModel) and extract any available metadata
        offers = db.query(OfferModel).filter(OfferModel.url.in_(urls_to_match)).all()
        offer_image = None
        offer_cond = None
        offer_grad = None
        offer_is_v = False
        offer_source = None
        offer_receipt = None

        for offer in offers:
            offer_image = offer.image_url or (offer.product.image_url if offer.product else None)
            offer_cond = offer.condition
            offer_grad = offer.grading
            offer_is_v = bool(offer.is_vintage)
            offer_source = offer.source_type
            offer_receipt = offer.receipt_id
            prod_id = offer.product_id

            db.delete(offer)
            db.flush()

            if prod_id and offer_is_v:
                rem = db.query(OfferModel).filter(
                    OfferModel.product_id == prod_id,
                    OfferModel.is_vintage == True
                ).count()
                if rem == 0:
                    prod = db.query(ProductModel).filter(ProductModel.id == prod_id).first()
                    if prod:
                        prod.is_vintage = False
                    db.query(VintageProductModel).filter(VintageProductModel.product_id == prod_id).delete()

        # 3. Clean up Vintage Miscellaneous (VintageMiscellaneousModel)
        misc_items = db.query(VintageMiscellaneousModel).filter(VintageMiscellaneousModel.url.in_(urls_to_match)).all()
        misc_title = None
        misc_image = None
        misc_cond = None
        misc_grad = None
        for misc in misc_items:
            misc_title = misc.title
            misc_image = misc.image_url
            misc_cond = misc.condition
            misc_grad = misc.grading
            db.delete(misc)

        # 4. Clean up ProductAliasModel
        db.query(ProductAliasModel).filter(ProductAliasModel.source_url.in_(urls_to_match)).delete(synchronize_session=False)

        # 5. Build full metadata for PendingMatchModel
        scraped_name = (
            (original_item.get("scraped_name") if original_item else None)
            or bl_scraped_name
            or misc_title
            or history.product_name
        )
        price = (original_item.get("price") if original_item else None) or history.price or 0.0
        shop_name = (original_item.get("shop_name") if original_item else None) or history.shop_name or "Desconocido"
        currency = (original_item.get("currency") if original_item else None) or "EUR"
        image_url = (original_item.get("image_url") if original_item else None) or offer_image or misc_image
        condition = (original_item.get("condition") if original_item else None) or offer_cond or misc_cond or "Loose"
        grading = (original_item.get("grading") if original_item else None) or offer_grad or misc_grad or 7.5
        source_type = (original_item.get("source_type") if original_item else None) or offer_source or bl_source_type or "Retail"
        is_vintage = (
            (original_item.get("is_vintage") if original_item else None)
            or offer_is_v
            or bool(misc_items)
            or ("VINTAGE" in history.action_type or "MISCELLANEOUS" in history.action_type)
        )
        receipt_id = (original_item.get("receipt_id") if original_item else None) or offer_receipt

        # 6. Recreate or update in PendingMatchModel idempotently
        existing_pending = db.query(PendingMatchModel).filter(PendingMatchModel.url.in_(urls_to_match)).first()
        if existing_pending:
            existing_pending.scraped_name = scraped_name
            existing_pending.price = price
            existing_pending.shop_name = shop_name
            existing_pending.currency = currency
            existing_pending.image_url = image_url or existing_pending.image_url
            existing_pending.condition = condition
            existing_pending.grading = grading
            existing_pending.source_type = source_type
            existing_pending.is_vintage = is_vintage
            existing_pending.receipt_id = receipt_id or existing_pending.receipt_id
            existing_pending.is_blocked = False
            existing_pending.validation_status = "PENDING"
        else:
            purgatory_item = PendingMatchModel(
                scraped_name=scraped_name,
                ean=(original_item.get("ean") if original_item else None),
                price=price,
                currency=currency,
                url=raw_url,
                shop_name=shop_name,
                image_url=image_url,
                condition=condition,
                grading=grading,
                source_type=source_type,
                is_vintage=is_vintage,
                receipt_id=receipt_id,
                validation_status="PENDING",
                is_blocked=False,
            )
            db.add(purgatory_item)

        db.delete(history)
        db.commit()

        return {"status": "success", "message": f"Justicia restaurada: '{scraped_name}' devuelto al Purgatorio"}
