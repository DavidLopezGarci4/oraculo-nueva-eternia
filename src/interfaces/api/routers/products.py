from collections import defaultdict
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import and_, desc, func, select

from src.application.services.deal_scorer import DealScorer
from src.application.services.logistics_service import LogisticsService
from src.domain.models import CollectionItemModel, OfferModel, ProductModel, UserModel
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_api_key, verify_device
from src.interfaces.api.schemas import ProductEditRequest, ProductMergeRequest, ProductOutput

router = APIRouter(tags=["products"])


@router.get("/api/products", response_model=List[ProductOutput])
async def get_products():
    with SessionCloud() as db:
        subq = (
            select(OfferModel.product_id, func.min(OfferModel.price).label("min_price"))
            .where(OfferModel.source_type == "Peer-to-Peer")
            .where(OfferModel.is_available == True)
            .group_by(OfferModel.product_id)
            .subquery()
        )

        query = (
            select(ProductModel, OfferModel)
            .outerjoin(subq, ProductModel.id == subq.c.product_id)
            .outerjoin(
                OfferModel,
                and_(
                    OfferModel.product_id == ProductModel.id,
                    OfferModel.price == subq.c.min_price,
                    OfferModel.source_type == "Peer-to-Peer",
                    OfferModel.is_available == True,
                ),
            )
        )

        results = db.execute(query).all()

        seen: set = set()
        final_products = []
        for product, best_offer in results:
            if product.id in seen:
                continue
            seen.add(product.id)
            po = ProductOutput.model_validate(product)
            po.avg_market_price = product.avg_market_price or 0.0
            if best_offer:
                po.best_p2p_price = best_offer.price
                po.best_p2p_source = best_offer.shop_name
            final_products.append(po)

        return final_products


@router.get("/api/products/search")
async def search_products(q: str = ""):
    if len(q) < 2:
        return []

    with SessionCloud() as db:
        query = select(ProductModel).where(
            (ProductModel.name.ilike(f"%{q}%")) | (ProductModel.figure_id.ilike(f"%{q}%"))
        ).limit(20)

        result = db.execute(query)
        products = result.scalars().all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "figure_id": p.figure_id,
                "sub_category": p.sub_category,
                "image_url": p.image_url,
            }
            for p in products
        ]


@router.get("/api/auctions/products", response_model=List[ProductOutput])
async def get_auction_products():
    with SessionCloud() as db:
        subq = (
            select(OfferModel.product_id, func.min(OfferModel.price).label("min_price"))
            .where(OfferModel.source_type == "Peer-to-Peer")
            .where(OfferModel.is_available == True)
            .group_by(OfferModel.product_id)
            .subquery()
        )

        query = (
            select(ProductModel, OfferModel)
            .join(subq, ProductModel.id == subq.c.product_id)
            .join(
                OfferModel,
                and_(
                    OfferModel.product_id == ProductModel.id,
                    OfferModel.price == subq.c.min_price,
                    OfferModel.source_type == "Peer-to-Peer",
                    OfferModel.is_available == True,
                ),
            )
        )

        results = db.execute(query).all()

        seen: set = set()
        output = []
        for product, best_offer in results:
            if product.id in seen:
                continue
            seen.add(product.id)
            p_out = ProductOutput.model_validate(product)
            p_out.best_p2p_price = best_offer.price
            p_out.best_p2p_source = best_offer.shop_name

            if p_out.avg_retail_price == 0 or p_out.avg_p2p_price == 0:
                offers = db.query(OfferModel).filter(
                    OfferModel.product_id == product.id, OfferModel.is_available == True
                ).all()
                retail_prices = [o.price for o in offers if o.source_type == "Retail"]
                p2p_prices = [o.price for o in offers if o.source_type == "Peer-to-Peer"]

                if retail_prices:
                    p_out.avg_retail_price = round(sum(retail_prices) / len(retail_prices), 2)
                if p2p_prices:
                    p_out.avg_p2p_price = round(sum(p2p_prices) / len(p2p_prices), 2)

            output.append(p_out)

        return output


@router.get("/api/intelligence/market/{product_id}", dependencies=[Depends(verify_api_key)])
async def get_market_intelligence(product_id: int):
    from src.application.services.market_intelligence import MarketIntelligenceService

    with SessionCloud() as db:
        service = MarketIntelligenceService(db)
        summary = service.get_market_summary(product_id)
        if not summary or summary == {}:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return summary


@router.get("/api/wallapop/preview", dependencies=[Depends(verify_api_key)])
async def get_wallapop_preview(url: str):
    from src.application.services.wallapop_bridge import WallapopBridge

    details = await WallapopBridge.get_item_details(url)
    if not details:
        raise HTTPException(status_code=404, detail="No se pudo invocar el espíritu de Wallapop")
    return details


@router.put("/api/products/{product_id}", dependencies=[Depends(verify_api_key)])
async def edit_product(product_id: int, request: ProductEditRequest):
    with SessionCloud() as db:
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        if request.name is not None:
            product.name = request.name
        if request.ean is not None:
            product.ean = request.ean
        if request.image_url is not None:
            product.image_url = request.image_url
        if request.category is not None:
            product.category = request.category
        if request.sub_category is not None:
            product.sub_category = request.sub_category
        if request.retail_price is not None:
            product.retail_price = request.retail_price

        db.commit()
        return {"status": "success", "message": f"Reliquia '{product.name}' actualizada con éxito"}


@router.post("/api/products/merge", dependencies=[Depends(verify_api_key)])
async def merge_products(request: ProductMergeRequest):
    with SessionCloud() as db:
        source = db.query(ProductModel).filter(ProductModel.id == request.source_id).first()
        target = db.query(ProductModel).filter(ProductModel.id == request.target_id).first()
        if not source or not target:
            raise HTTPException(status_code=404, detail="Producto(s) no encontrado")

        db.query(OfferModel).filter(OfferModel.product_id == source.id).update({"product_id": target.id})

        source_items = db.query(CollectionItemModel).filter(CollectionItemModel.product_id == source.id).all()
        for item in source_items:
            exists = db.query(CollectionItemModel).filter(
                CollectionItemModel.product_id == target.id,
                CollectionItemModel.owner_id == item.owner_id,
            ).first()
            if not exists:
                item.product_id = target.id
            else:
                db.delete(item)

        source_name = source.name
        db.delete(source)
        db.commit()
        return {"status": "success", "message": f"Fusión divina: '{source_name}' ha sido absorbido por '{target.name}'"}


@router.get("/api/products/with-offers", dependencies=[Depends(verify_device)])
async def get_products_with_offers():
    with SessionCloud() as db:
        product_ids = (
            db.query(OfferModel.product_id)
            .filter(OfferModel.product_id.isnot(None), OfferModel.is_available == True)
            .distinct()
            .all()
        )
        return [p[0] for p in product_ids]


@router.get("/api/products/{product_id}/offers", dependencies=[Depends(verify_device)])
async def get_product_offers(product_id: int):
    with SessionCloud() as db:
        all_offers = (
            db.query(OfferModel)
            .filter(OfferModel.product_id == product_id, OfferModel.is_available == True)
            .order_by(OfferModel.price.asc(), desc(OfferModel.last_seen))
            .all()
        )

        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == 1).first()
        if user:
            user_location = user.location

        latest_by_shop = {}
        for o in all_offers:
            if o.shop_name not in latest_by_shop:
                landing_p = LogisticsService.get_landing_price(o.price, o.shop_name, user_location)
                latest_by_shop[o.shop_name] = {
                    "id": o.id,
                    "shop_name": o.shop_name,
                    "price": o.price,
                    "landing_price": landing_p,
                    "url": o.url,
                    "last_seen": o.last_seen.isoformat(),
                    "min_historical": o.min_price or o.price,
                    "opportunity_score": o.opportunity_score,
                    "source_type": o.source_type,
                    "is_best": False,
                    "is_available": o.is_available,
                    "sale_type": o.sale_type,
                    "expiry_at": o.expiry_at.isoformat() if o.expiry_at else None,
                    "bids_count": o.bids_count,
                    "time_left_raw": o.time_left_raw,
                }

        results = list(latest_by_shop.values())
        if results:
            results.sort(key=lambda x: x["landing_price"])
            results[0]["is_best"] = True

        return results


@router.get("/api/market/analytics/{product_id}")
async def get_market_analytics(product_id: int):
    with SessionCloud() as db:
        offers = db.query(OfferModel).filter(
            OfferModel.product_id == product_id, OfferModel.is_available == True
        ).all()

        retail_prices = [o.price for o in offers if o.source_type == "Retail"]
        p2p_prices = [o.price for o in offers if o.source_type == "Peer-to-Peer"]

        def get_stats(prices):
            if not prices:
                return {"avg": 0, "min": 0, "max": 0, "count": 0}
            return {
                "avg": round(sum(prices) / len(prices), 2),
                "min": min(prices),
                "max": max(prices),
                "count": len(prices),
            }

        return {
            "retail": get_stats(retail_prices),
            "p2p": get_stats(p2p_prices),
            "global_avg": get_stats(retail_prices + p2p_prices)["avg"],
        }


@router.get("/api/products/{product_id}/price-history")
async def get_product_price_history(product_id: int):
    from src.domain.models import PriceHistoryModel

    with SessionCloud() as db:
        offers = db.query(OfferModel).filter(OfferModel.product_id == product_id).all()

        shop_groups = defaultdict(list)
        for offer in offers:
            history = (
                db.query(PriceHistoryModel)
                .filter(PriceHistoryModel.offer_id == offer.id)
                .order_by(PriceHistoryModel.recorded_at.asc())
                .all()
            )
            for h in history:
                date_key = h.recorded_at.date().isoformat()
                shop_groups[offer.shop_name].append({
                    "date": date_key,
                    "price": h.price,
                    "timestamp": h.recorded_at,
                })

        results = []
        for shop_name, history_points in shop_groups.items():
            daily_best = {}
            for p in history_points:
                date = p["date"]
                if date not in daily_best or p["price"] < daily_best[date]["price"]:
                    daily_best[date] = p

            sorted_history = sorted(daily_best.values(), key=lambda x: x["timestamp"])
            results.append({
                "shop_name": shop_name,
                "history": [{"date": p["date"], "price": p["price"]} for p in sorted_history],
            })

        results.sort(key=lambda x: x["shop_name"])
        return results
