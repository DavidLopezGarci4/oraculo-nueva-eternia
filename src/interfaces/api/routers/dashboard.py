import json
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import and_, desc, func

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
async def get_dashboard_stats(user_id: int = 1):
    try:
        with SessionCloud() as db:
            # Total products counts (Agrupado por is_vintage para ahorrar 1 query)
            product_counts = db.query(
                ProductModel.is_vintage,
                func.count(ProductModel.id)
            ).group_by(
                ProductModel.is_vintage
            ).all()
            
            total_products = 0
            total_products_vintage = 0
            for is_vintage, cnt in product_counts:
                if is_vintage:
                    total_products_vintage = cnt
                else:
                    total_products = cnt

            # Collection counts (owned vs wishlist, modern vs vintage) agrupados para ahorrar 3 queries
            coll_counts = db.query(
                CollectionItemModel.acquired,
                ProductModel.is_vintage,
                func.count(CollectionItemModel.id)
            ).join(ProductModel).filter(
                CollectionItemModel.owner_id == user_id
            ).group_by(
                CollectionItemModel.acquired,
                ProductModel.is_vintage
            ).all()

            owned_count = 0
            owned_count_vintage = 0
            wish_count = 0
            wish_count_vintage = 0

            for acquired, is_vintage, cnt in coll_counts:
                if acquired:
                    if is_vintage:
                        owned_count_vintage = cnt
                    else:
                        owned_count = cnt
                else:
                    if is_vintage:
                        wish_count_vintage = cnt
                    else:
                        wish_count = cnt

            from src.application.services.valuation_service import ValuationService

            valuation_service = ValuationService(db)
            user_location = "ES"
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if user:
                user_location = user.location

            financials = valuation_service.get_collection_valuation(user_id, user_location, is_vintage=False)
            financials_vintage = valuation_service.get_collection_valuation(user_id, user_location, is_vintage=True)

            total_invested = financials["total_invested"]
            market_value = financials["total_value"]
            profit_loss = financials["profit_loss"]
            roi = financials["roi"]

            total_invested_v = financials_vintage["total_invested"]
            market_value_v = financials_vintage["total_value"]
            profit_loss_v = financials_vintage["profit_loss"]
            roi_v = financials_vintage["roi"]

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
                    "profit_loss": round(profit_loss, 2),
                    "roi": round(roi, 1),
                },
                "financial_vintage": {
                    "total_invested": round(total_invested_v, 2),
                    "market_value": round(market_value_v, 2),
                    "profit_loss": round(profit_loss_v, 2),
                    "roi": round(roi_v, 1),
                },
                "match_count": match_count,
                "shop_distribution": [{"shop": s, "count": c} for s, c in shop_dist],
            }

    except Exception as e:
        logger.error(f"CRITICAL DASHBOARD ERROR for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al recuperar datos del tablero: {str(e)}")


@router.get("/hall-of-fame", response_model=HallOfFameOutput, dependencies=[Depends(verify_device)])
async def get_dashboard_hall_of_fame(user_id: int = 1):
    with SessionCloud() as db:
        items = (
            db.query(CollectionItemModel)
            .join(ProductModel)
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
async def get_top_deals(user_id: int = 2):
    with SessionCloud() as db:
        owned_ids = [
            p[0]
            for p in db.query(CollectionItemModel.product_id).filter(
                CollectionItemModel.owner_id == user_id,
                CollectionItemModel.acquired == True,
            ).all()
        ]

        freshness_threshold = datetime.now(timezone.utc) - timedelta(hours=72)

        rules = db.query(LogisticRuleModel).all()
        rules_map = {f"{r.shop_name}_{r.country_code}": r for r in rules}

        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            user_location = user.location

        # Consultar ofertas candidatas activas sin filtro SQL prematuro de MIN(price)
        query = (
            db.query(OfferModel)
            .join(ProductModel)
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

        # Agrupar por producto y seleccionar la oferta con el menor Landed Price real
        best_by_product = {}
        for o in all_candidate_offers:
            if not o.product:
                continue
            landing_p = LogisticsService.optimized_get_landing_price(o.price, o.shop_name, user_location, rules_map)
            retail = float(o.product.retail_price or 19.99)
            base_p = float(o.price)
            # Calcular descuento respecto al PVP oficial usando el precio base de tienda o landed
            ref_price = min(landing_p, base_p)
            discount = max(0.0, round(((retail - ref_price) / retail) * 100, 1)) if retail > 0 else 0.0

            item_data = {
                "id": o.id,
                "product_id": o.product_id,
                "product_name": o.product.name,
                "price": o.price,
                "landing_price": landing_p,
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
                if landing_p < current_best["landing_price"] or (
                    abs(landing_p - current_best["landing_price"]) < 0.01 and o.opportunity_score > current_best["opportunity_score"]
                ):
                    best_by_product[o.product_id] = item_data

        deals = list(best_by_product.values())
        deals.sort(key=lambda x: (x["landing_price"], -x["opportunity_score"]))

        seen_names = set()
        final_deals = []
        for r in deals:
            if r["product_name"] not in seen_names:
                seen_names.add(r["product_name"])
                final_deals.append(r)

        return final_deals[:20]


@router.get("/match-stats", response_model=List[MatchStatOutput], dependencies=[Depends(verify_device)])
async def get_dashboard_match_stats():
    with SessionCloud() as db:
        stats = (
            db.query(OfferModel.shop_name.label("shop"), func.count(OfferModel.id).label("count"))
            .filter(OfferModel.product_id.isnot(None), OfferModel.is_available == True)
            .group_by(OfferModel.shop_name)
            .all()
        )

        return [{"shop": s.shop, "count": s.count} for s in stats]


@router.get("/history", response_model=List[MatchHistoryOutput], dependencies=[Depends(verify_device)])
async def get_dashboard_history():
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
async def revert_action(request: dict):
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

