from collections import defaultdict
from typing import List
import time
import threading

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import and_, desc, func, select, event

from src.application.services.deal_scorer import DealScorer
from src.application.services.logistics_service import LogisticsService
from src.domain.models import CollectionItemModel, OfferModel, ProductModel, UserModel, PendingMatchModel
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_api_key, verify_device
from src.interfaces.api.schemas import ProductEditRequest, ProductMergeRequest, ProductOutput

router = APIRouter(tags=["products"])

# Variables de caché en memoria para los emparejamientos del Purgatorio
_purgatory_counts_cache = None
_purgatory_counts_timestamp = 0.0
_purgatory_counts_lock = threading.Lock()

def clear_purgatory_counts_cache():
    global _purgatory_counts_cache, _purgatory_counts_timestamp
    with _purgatory_counts_lock:
        _purgatory_counts_cache = None
        _purgatory_counts_timestamp = 0.0
    logger.info("Purgatory match counts cache CLEARED reactively.")

# Invalidar caché reactivamente cuando cambie la base de datos
@event.listens_for(PendingMatchModel, 'after_insert')
@event.listens_for(PendingMatchModel, 'after_update')
@event.listens_for(PendingMatchModel, 'after_delete')
@event.listens_for(ProductModel, 'after_insert')
@event.listens_for(ProductModel, 'after_delete')
def on_db_change(mapper, connection, target):
    clear_purgatory_counts_cache()


def get_purgatory_counts(db) -> dict[int, int]:
    global _purgatory_counts_cache, _purgatory_counts_timestamp
    
    with _purgatory_counts_lock:
        now = time.time()
        if _purgatory_counts_cache is not None and (now - _purgatory_counts_timestamp) < 60:
            return _purgatory_counts_cache

    from src.domain.models import PendingMatchModel, ProductModel
    from src.core.brain_engine import engine
    import re

    pending = db.query(PendingMatchModel).all()
    products = db.query(ProductModel).all()

    _STOP_WORDS = {"masters", "of", "the", "universe", "origins", "motu"}

    # Build token index
    token_index = {}
    ean_index = {}
    for p in products:
        for token in set(re.findall(r"\w+", (p.name or "").lower())) - _STOP_WORDS:
            token_index.setdefault(token, []).append(p)
        if p.ean:
            ean_index.setdefault(p.ean, []).append(p)

    counts = {}
    for item in pending:
        scraped_name_safe = (item.scraped_name or "").lower()
        search_tokens = set(re.findall(r"\w+", scraped_name_safe)) - _STOP_WORDS

        candidates = set()
        for token in search_tokens:
            candidates.update(token_index.get(token, []))
        if item.ean:
            candidates.update(ean_index.get(item.ean, []))

        for p in candidates:
            _, score, _ = engine.calculate_match(p.name, item.scraped_name, p.ean, item.ean)
            if score > 0.30:
                counts[p.id] = counts.get(p.id, 0) + 1

    with _purgatory_counts_lock:
        _purgatory_counts_cache = counts
        _purgatory_counts_timestamp = time.time()

    return counts


@router.get("/api/products", response_model=List[ProductOutput])
async def get_products(is_vintage: bool = False):
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
        if is_vintage:
            query = query.where(ProductModel.is_vintage == True)
        else:
            query = query.where(ProductModel.is_vintage.is_not(True))

        results = db.execute(query).all()
        counts = get_purgatory_counts(db)

        seen: set = set()
        final_products = []
        for product, best_offer in results:
            if product.id in seen:
                continue
            seen.add(product.id)
            po = ProductOutput.model_validate(product)
            po.avg_market_price = product.avg_market_price or 0.0
            po.purgatory_match_count = counts.get(product.id, 0)
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
async def get_auction_products(is_vintage: bool = False):
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
        if is_vintage:
            query = query.where(ProductModel.is_vintage == True)
        else:
            query = query.where(ProductModel.is_vintage.is_not(True))

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
    from src.domain.models import VintageProductModel
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
            
        if request.is_vintage is not None:
            product.is_vintage = request.is_vintage
            
            # Sync is_vintage to all linked offers!
            db.query(OfferModel).filter(OfferModel.product_id == product.id).update({"is_vintage": request.is_vintage})
            
            # Sync to VintageProductModel
            if request.is_vintage:
                # Ensure a VintageProductModel entry exists
                exists = db.query(VintageProductModel).filter(VintageProductModel.product_id == product.id).first()
                if not exists:
                    vintage_entry = VintageProductModel(product_id=product.id, notes="Promoted via metadata update")
                    db.add(vintage_entry)
            else:
                # Remove from VintageProductModel if it exists
                db.query(VintageProductModel).filter(VintageProductModel.product_id == product.id).delete()

        db.commit()
        return {"status": "success", "message": f"Reliquia '{product.name}' actualizada con éxito"}


@router.post("/api/products/merge", dependencies=[Depends(verify_api_key)])
async def merge_products(request: ProductMergeRequest):
    from src.domain.models import ProductAliasModel, VintageProductModel, PriceAlertModel

    with SessionCloud() as db:
        source = db.query(ProductModel).filter(ProductModel.id == request.source_id).first()
        target = db.query(ProductModel).filter(ProductModel.id == request.target_id).first()
        if not source or not target:
            raise HTTPException(status_code=404, detail="Producto(s) no encontrado")

        # 1. Transfer offers
        db.query(OfferModel).filter(OfferModel.product_id == source.id).update({"product_id": target.id})

        # 2. Transfer collection items (preventing duplicates)
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

        # 3. Transfer/deduplicate aliases
        source_aliases = db.query(ProductAliasModel).filter(ProductAliasModel.product_id == source.id).all()
        for alias in source_aliases:
            exists = db.query(ProductAliasModel).filter(
                ProductAliasModel.product_id == target.id,
                ProductAliasModel.source_url == alias.source_url
            ).first()
            if not exists:
                alias.product_id = target.id
            else:
                db.delete(alias)

        # 4. Transfer/deduplicate price alerts
        source_alerts = db.query(PriceAlertModel).filter(PriceAlertModel.product_id == source.id).all()
        for alert in source_alerts:
            exists = db.query(PriceAlertModel).filter(
                PriceAlertModel.product_id == target.id,
                PriceAlertModel.user_id == alert.user_id
            ).first()
            if not exists:
                alert.product_id = target.id
            else:
                db.delete(alert)

        # 5. Transfer/deduplicate vintage product entry
        source_vintage = db.query(VintageProductModel).filter(VintageProductModel.product_id == source.id).first()
        if source_vintage:
            exists = db.query(VintageProductModel).filter(VintageProductModel.product_id == target.id).first()
            if not exists:
                source_vintage.product_id = target.id
            else:
                db.delete(source_vintage)

        # 6. Delete source product
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


@router.get("/api/products/shops")
async def get_unique_shops():
    with SessionCloud() as db:
        query = select(OfferModel.shop_name).distinct()
        results = db.execute(query).scalars().all()
        shops = sorted(list(set([r for r in results if r])))
        return shops


@router.get("/api/vintage/products")
async def get_vintage_products():
    with SessionCloud() as db:
        # Fetch all offers marked as is_vintage to list them individually
        query = (
            select(OfferModel, ProductModel)
            .join(ProductModel, OfferModel.product_id == ProductModel.id)
            .where(OfferModel.is_vintage == True)
            .where(OfferModel.is_available == True)
            .order_by(OfferModel.price.asc())
        )

        results = db.execute(query).all()

        output = []
        for offer, product in results:
            output.append({
                "id": product.id,
                "name": product.name,
                "ean": product.ean,
                "image_url": offer.image_url or product.image_url,
                "category": product.category,
                "sub_category": product.sub_category,
                "figure_id": product.figure_id,
                "release_year": product.release_year,
                
                # Offer specific individual fields
                "offer_id": offer.id,
                "best_p2p_price": offer.price,
                "best_p2p_source": offer.shop_name,
                "url": offer.url,
                "condition": offer.condition or "Loose",
                "grading": offer.grading or 7.5,
                "bids_count": offer.bids_count,
                "time_left_raw": offer.time_left_raw,
                "sale_type": offer.sale_type
            })

        return output


@router.delete("/api/products/{product_id}", dependencies=[Depends(verify_api_key)])
async def delete_product(product_id: int):
    from src.domain.models import OfferModel, PendingMatchModel, ProductAliasModel, ProductModel, VintageProductModel, PriceAlertModel
    
    with SessionCloud() as db:
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
            
        product_name = product.name
        
        # 1. Obtener todas las ofertas vinculadas a este producto para devolverlas al Purgatorio
        offers = db.query(OfferModel).filter(OfferModel.product_id == product.id).all()
        for offer in offers:
            purgatory_item = PendingMatchModel(
                scraped_name=offer.product.name if offer.product else product_name,
                ean=product.ean,
                price=offer.price,
                currency=offer.currency,
                url=offer.url,
                shop_name=offer.shop_name,
                image_url=offer.image_url,
                source_type=offer.source_type,
                is_vintage=offer.is_vintage,
                condition=offer.condition or "Loose",
                grading=offer.grading or 7.5
            )
            db.add(purgatory_item)
            
            # Borrar alias de este item
            db.query(ProductAliasModel).filter(ProductAliasModel.source_url == offer.url).delete()
            
        # 2. Borrar las ofertas del producto
        db.query(OfferModel).filter(OfferModel.product_id == product.id).delete()
        
        # 3. Borrar de VintageProductModel si existía
        db.query(VintageProductModel).filter(VintageProductModel.product_id == product.id).delete()
        
        # 4. Borrar todos los alias restantes vinculados a este product_id
        db.query(ProductAliasModel).filter(ProductAliasModel.product_id == product.id).delete()
        
        # 5. Borrar alertas de precios vinculadas a este product_id
        db.query(PriceAlertModel).filter(PriceAlertModel.product_id == product.id).delete()
        
        # 6. Borrar colecciones/lista de deseos vinculadas a este product_id
        db.query(CollectionItemModel).filter(CollectionItemModel.product_id == product.id).delete()
        
        # 7. Eliminar el producto genérico por completo de la base de datos
        db.delete(product)
        
        db.commit()
        return {
            "status": "success", 
            "message": f"Producto '{product_name}' eliminado de Eternia con éxito. {len(offers)} ofertas devueltas al Purgatorio."
        }


@router.get("/api/vintage/miscellaneous")
async def get_vintage_miscellaneous():
    with SessionCloud() as db:
        from src.domain.models import VintageMiscellaneousModel
        results = db.query(VintageMiscellaneousModel).order_by(desc(VintageMiscellaneousModel.added_at)).all()
        
        output = []
        for item in results:
            output.append({
                "id": item.id,
                "title": item.title,
                "url": item.url,
                "price": item.price,
                "currency": item.currency,
                "shop_name": item.shop_name,
                "image_url": item.image_url,
                "condition": item.condition or "Loose",
                "grading": item.grading or 7.5,
                "notes": item.notes,
                "added_at": item.added_at.isoformat() if item.added_at else None
            })
        return output


