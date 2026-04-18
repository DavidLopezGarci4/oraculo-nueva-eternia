import json
from datetime import datetime, timedelta

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
from src.interfaces.api.deps import verify_device

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", dependencies=[Depends(verify_device)])
async def get_dashboard_stats(user_id: int = 1):
    try:
        with SessionCloud() as db:
            total_products = db.query(ProductModel).count()
            owned_count = db.query(CollectionItemModel).filter(
                CollectionItemModel.owner_id == user_id,
                CollectionItemModel.acquired == True,
            ).count()

            wish_count = db.query(CollectionItemModel).filter(
                CollectionItemModel.owner_id == user_id,
                CollectionItemModel.acquired == False,
            ).count()

            from src.application.services.valuation_service import ValuationService

            valuation_service = ValuationService(db)
            user_location = "ES"
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if user:
                user_location = user.location

            financials = valuation_service.get_collection_valuation(user_id, user_location)

            total_invested = financials["total_invested"]
            market_value = financials["total_value"]
            profit_loss = financials["profit_loss"]
            roi = financials["roi"]

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
                "owned_count": owned_count,
                "wish_count": wish_count,
                "financial": {
                    "total_invested": round(total_invested, 2),
                    "market_value": round(market_value, 2),
                    "profit_loss": round(profit_loss, 2),
                    "roi": round(roi, 1),
                },
                "match_count": match_count,
                "shop_distribution": [{"shop": s, "count": c} for s, c in shop_dist],
            }
    except Exception as e:
        logger.error(f"CRITICAL DASHBOARD ERROR for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al recuperar datos del tablero: {str(e)}")


@router.get("/hall-of-fame", dependencies=[Depends(verify_device)])
async def get_dashboard_hall_of_fame(user_id: int = 1):
    with SessionCloud() as db:
        items = (
            db.query(CollectionItemModel)
            .join(ProductModel)
            .filter(CollectionItemModel.acquired == True, CollectionItemModel.owner_id == user_id)
            .all()
        )

        if not items:
            return {"top_value": [], "top_roi": []}

        from src.application.services.valuation_service import ValuationService

        valuation_service = ValuationService(db)

        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            user_location = user.location

        analyzed_items = []
        for item in items:
            market_val = valuation_service.get_consolidated_value(item.product, user_location)
            invested = item.purchase_price or 0.0

            roi = 0.0
            if invested > 0:
                roi = ((market_val - invested) / invested) * 100

            analyzed_items.append({
                "id": item.product.id,
                "name": item.product.name,
                "image_url": item.product.image_url,
                "figure_id": item.product.figure_id,
                "market_value": round(market_val, 2),
                "purchase_price": invested,
                "roi": round(roi, 1),
            })

        top_value = sorted(analyzed_items, key=lambda x: x["market_value"], reverse=True)[:5]
        top_roi = sorted(analyzed_items, key=lambda x: x["roi"], reverse=True)[:5]

        return {
            "top_value": top_value,
            "top_roi": [i for i in top_roi if i["roi"] > 0],
        }


@router.get("/top-deals", dependencies=[Depends(verify_device)])
async def get_top_deals(user_id: int = 2):
    with SessionCloud() as db:
        owned_ids = [
            p[0]
            for p in db.query(CollectionItemModel.product_id).filter(
                CollectionItemModel.owner_id == user_id,
                CollectionItemModel.acquired == True,
            ).all()
        ]

        freshness_threshold = datetime.utcnow() - timedelta(hours=72)

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


@router.get("/match-stats")
async def get_dashboard_match_stats():
    with SessionCloud() as db:
        stats = (
            db.query(OfferModel.shop_name.label("shop"), func.count(OfferModel.id).label("count"))
            .filter(OfferModel.product_id.isnot(None), OfferModel.is_available == True)
            .group_by(OfferModel.shop_name)
            .all()
        )

        return [{"shop": s.shop, "count": s.count} for s in stats]


@router.get("/history")
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


@router.post("/revert")
async def revert_action(request: dict):
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
