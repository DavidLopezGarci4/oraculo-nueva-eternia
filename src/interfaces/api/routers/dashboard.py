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
            
            # Cálculo de precio original: purchase_price con fallbacks a retail_price u avg_market_price
            invested = item.purchase_price or 0.0
            if invested == 0.0 and item.product.retail_price:
                invested = item.product.retail_price
            if invested == 0.0 and item.product.avg_market_price:
                invested = item.product.avg_market_price

            roi = 0.0
            if invested > 0:
                roi = ((market_val - invested) / invested) * 100

            data = {
                "id": item.product.id,
                "name": item.product.name,
                "image_url": item.product.image_url,
                "figure_id": item.product.figure_id,
                "market_value": round(market_val, 2),
                "purchase_price": round(invested, 2),
                "invested_value": round(invested, 2),  # Compatibilidad frontend
                "roi": round(roi, 1),
                "roi_percentage": round(roi, 1),  # Compatibilidad frontend
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

        best_prices_subq = (
            db.query(OfferModel.product_id, func.min(OfferModel.price).label("min_price"))
            .filter(
                OfferModel.is_available == True,
                OfferModel.last_seen >= freshness_threshold,
                OfferModel.source_type == "Retail",
                OfferModel.product_id.notin_(owned_ids) if owned_ids else True,
            )
            .group_by(OfferModel.product_id)
            .subquery()
        )

        offers = (
            db.query(OfferModel)
            .join(
                best_prices_subq,
                and_(
                    OfferModel.product_id == best_prices_subq.c.product_id,
                    OfferModel.price == best_prices_subq.c.min_price,
                ),
            )
            .join(ProductModel)
            .filter(
                OfferModel.is_available == True,
                OfferModel.last_seen >= freshness_threshold,
                OfferModel.opportunity_score > 0,
            )
            .order_by(OfferModel.opportunity_score.desc())
        )

        rules = db.query(LogisticRuleModel).all()
        rules_map = {f"{r.shop_name}_{r.country_code}": r for r in rules}

        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            user_location = user.location

        offers_pool = offers.limit(50).all()

        results = []
        for o in offers_pool:
            landing_p = LogisticsService.optimized_get_landing_price(o.price, o.shop_name, user_location, rules_map)
            results.append({
                "id": o.id,
                "product_id": o.product_id,
                "product_name": o.product.name,
                "price": o.price,
                "landing_price": landing_p,
                "shop_name": o.shop_name,
                "url": o.url,
                "opportunity_score": o.opportunity_score,
                "image_url": o.product.image_url,
            })

        results.sort(key=lambda x: x["landing_price"])

        seen_names = set()
        final_deals = []
        for r in results:
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
    # Fase AAA-2.1: esta acción borra/reconstruye entradas de OfferModel,
    # BlackcludedItemModel e historial — no tenía NINGUNA protección. Se alinea
    # con el resto de herramientas de curación (purgatory.py), que exigen
    # admin.
    history_id = request.get("history_id")
    if not history_id:
        raise HTTPException(status_code=400, detail="ID de historial requerido")

    with SessionCloud() as db:
        history = db.query(OfferHistoryModel).filter(OfferHistoryModel.id == history_id).first()
        if not history:
            raise HTTPException(status_code=404, detail="Entrada de historial no encontrada")

        original_item = None
        try:
            details_json = json.loads(history.details)
            if isinstance(details_json, dict):
                original_item = details_json.get("original_item")
        except Exception:
            logger.warning(f"Reconstruction Fallback for History ID {history_id}: No JSON metadata found.")

        if not original_item:
            original_item = {
                "scraped_name": history.product_name,
                "ean": None,
                "price": history.price,
                "currency": "EUR",
                "url": history.offer_url,
                "shop_name": history.shop_name,
                "image_url": None,
                "receipt_id": None,
            }

        if history.action_type in ["LINKED_MANUAL", "SMART_MATCH", "UPDATE"]:
            offer = db.query(OfferModel).filter(OfferModel.url == history.offer_url).first()
            if offer:
                db.delete(offer)

        elif history.action_type == "DISCARDED":
            bl = db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url == history.offer_url).first()
            if bl:
                db.delete(bl)

        purgatory_item = PendingMatchModel(
            scraped_name=original_item["scraped_name"],
            ean=original_item.get("ean"),
            price=original_item["price"],
            currency=original_item.get("currency", "EUR"),
            url=original_item["url"],
            shop_name=original_item["shop_name"],
            image_url=original_item.get("image_url"),
            receipt_id=original_item.get("receipt_id"),
        )
        db.add(purgatory_item)

        db.delete(history)
        db.commit()

        return {"status": "success", "message": f"Justicia restaurada: '{history.product_name}' devuelto al Purgatorio"}
