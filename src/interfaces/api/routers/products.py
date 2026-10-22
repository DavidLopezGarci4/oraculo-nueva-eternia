from collections import defaultdict
from datetime import datetime
from typing import List, Optional
import time
import threading

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import and_, desc, func, select, event
from sqlalchemy.orm import joinedload

from src.application.services.deal_scorer import DealScorer
from src.application.services.logistics_service import LogisticsService
from src.domain.models import (
    CollectionItemModel,
    LogisticRuleModel,
    OfferModel,
    PendingMatchModel,
    ProductLoreModel,
    ProductModel,
    UserModel,
)
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_api_key, verify_device
from src.interfaces.api.schemas import (
    ProductEditRequest,
    ProductMergeRequest,
    ProductOutput,
    ProductSearchResultOutput,
    StatusMessageOutput,
    ProductOfferOutput,
    MarketAnalyticsOutput,
    ProductPriceHistoryOutput,
    VintageProductListingOutput,
    VintageMiscellaneousItemOutput,
)

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
    try:
        from src.application.services.market_analytics_service import MarketAnalyticsService
        MarketAnalyticsService.invalidate_market_index_cache()
    except Exception:
        pass
    logger.info("Purgatory match counts cache CLEARED reactively.")


# Invalidar caché reactivamente cuando cambie la base de datos
@event.listens_for(PendingMatchModel, 'after_insert')
@event.listens_for(PendingMatchModel, 'after_update')
@event.listens_for(PendingMatchModel, 'after_delete')
@event.listens_for(ProductModel, 'after_insert')
@event.listens_for(ProductModel, 'after_delete')
def on_db_change(mapper, connection, target):
    # Throttle: solo invalidar si han transcurrido más de 60s para no degradar consultas durante scraping masivo
    if time.time() - _purgatory_counts_timestamp > 60:
        clear_purgatory_counts_cache()


def get_purgatory_counts(db) -> dict[int, int]:
    global _purgatory_counts_cache, _purgatory_counts_timestamp

    with _purgatory_counts_lock:
        now = time.time()
        if _purgatory_counts_cache is not None and (now - _purgatory_counts_timestamp) < 600:
            return _purgatory_counts_cache

        from src.domain.models import PendingMatchModel, ProductModel
        # Mismo motor y mismas predicciones que GET /api/purgatory (sin memoria ni acompañantes)
        from src.interfaces.api.routers.purgatory import build_suggestion_context, compute_suggestions

        pending = db.query(PendingMatchModel).all()
        products = db.query(ProductModel).all()
        ctx = build_suggestion_context(products)

        counts = {}
        for item in pending:
            for sug in compute_suggestions(item, ctx, use_memory=False):
                if sug.get("is_companion"):
                    continue
                pid = sug["product_id"]
                counts[pid] = counts.get(pid, 0) + 1

        _purgatory_counts_cache = counts
        _purgatory_counts_timestamp = time.time()
        return counts


@router.get("/api/products", response_model=List[ProductOutput])
def get_products(
    is_vintage: bool = False,
    shop: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    search: Optional[str] = None
):
    with SessionCloud() as db:
        query = select(ProductModel)
        if is_vintage:
            query = query.where(ProductModel.is_vintage == True)
        else:
            query = query.where(ProductModel.is_vintage.is_not(True))

        if search:
            search_term = f"%{search}%"
            query = query.where(
                ProductModel.name.ilike(search_term) |
                ProductModel.figure_id.ilike(search_term) |
                ProductModel.upc.ilike(search_term) |
                ProductModel.asin.ilike(search_term)
            )

        if shop:
            shop_exists_subq = (
                select(OfferModel.product_id)
                .where(OfferModel.shop_name == shop)
                .where(OfferModel.is_available == True)
            )
            query = query.where(ProductModel.id.in_(shop_exists_subq))

        query = query.order_by(ProductModel.id.asc())
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        products = db.execute(query).scalars().all()
        counts = get_purgatory_counts(db)

        best_p2p_by_pid: dict[int, tuple[float, str]] = {}
        if products:
            product_ids = [p.id for p in products]
            p2p_rows = (
                db.query(OfferModel.product_id, OfferModel.price, OfferModel.shop_name)
                .filter(
                    OfferModel.product_id.in_(product_ids),
                    OfferModel.source_type == "Peer-to-Peer",
                    OfferModel.is_available == True,
                )
                .order_by(OfferModel.product_id.asc(), OfferModel.price.asc())
                .all()
            )
            for pid, price, shop_name in p2p_rows:
                if pid not in best_p2p_by_pid:
                    best_p2p_by_pid[pid] = (price, shop_name)

        final_products = []
        for product in products:
            po = ProductOutput.model_validate(product)
            po.avg_market_price = product.avg_market_price or 0.0
            po.purgatory_match_count = counts.get(product.id, 0)
            best_p2p = best_p2p_by_pid.get(product.id)
            if best_p2p is not None:
                po.best_p2p_price = best_p2p[0]
                po.best_p2p_source = best_p2p[1]
            final_products.append(po)

        return final_products


@router.get("/api/products/search", response_model=List[ProductSearchResultOutput])
def search_products(q: str = ""):
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
def get_auction_products(is_vintage: bool = False):
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

        # Preload offers in a single batch for products missing avg_retail_price or avg_p2p_price
        missing_avg_pids = [
            product.id
            for product, _ in results
            if (product.avg_retail_price or 0) == 0 or (product.avg_p2p_price or 0) == 0
        ]
        offers_by_pid: dict[int, list[OfferModel]] = defaultdict(list)
        if missing_avg_pids:
            batch_offers = (
                db.query(OfferModel)
                .filter(
                    OfferModel.product_id.in_(missing_avg_pids),
                    OfferModel.is_available == True,
                )
                .all()
            )
            for o in batch_offers:
                offers_by_pid[o.product_id].append(o)

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
                offers = offers_by_pid.get(product.id, [])
                retail_prices = [o.price for o in offers if o.source_type == "Retail"]
                p2p_prices = [o.price for o in offers if o.source_type == "Peer-to-Peer"]

                if retail_prices:
                    p_out.avg_retail_price = round(sum(retail_prices) / len(retail_prices), 2)
                if p2p_prices:
                    p_out.avg_p2p_price = round(sum(p2p_prices) / len(p2p_prices), 2)

            output.append(p_out)

        return output


@router.get("/api/intelligence/market/{product_id}", dependencies=[Depends(verify_api_key)])
def get_market_intelligence(product_id: int):
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


@router.put("/api/products/{product_id}", response_model=StatusMessageOutput, dependencies=[Depends(verify_api_key)])
def edit_product(product_id: int, request: ProductEditRequest):
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


@router.post("/api/products/merge", response_model=StatusMessageOutput, dependencies=[Depends(verify_api_key)])
def merge_products(request: ProductMergeRequest):
    from src.domain.models import ProductAliasModel, VintageProductModel, PriceAlertModel

    with SessionCloud() as db:
        source = db.query(ProductModel).filter(ProductModel.id == request.source_id).first()
        target = db.query(ProductModel).filter(ProductModel.id == request.target_id).first()
        if not source or not target:
            raise HTTPException(status_code=404, detail="Producto(s) no encontrado")

        # 1. Transfer offers & align division alignment (is_vintage)
        db.query(OfferModel).filter(OfferModel.product_id == source.id).update({
            "product_id": target.id,
            "is_vintage": target.is_vintage
        })

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

        # 5b. Transfer/deduplicate product lore entry
        source_lore = db.query(ProductLoreModel).filter(ProductLoreModel.product_id == source.id).first()
        if source_lore:
            exists = db.query(ProductLoreModel).filter(ProductLoreModel.product_id == target.id).first()
            if not exists:
                source_lore.product_id = target.id
            else:
                db.delete(source_lore)

        # 6. Delete source product
        source_name = source.name
        db.delete(source)
        db.commit()
        return {"status": "success", "message": f"Fusión divina: '{source_name}' ha sido absorbido por '{target.name}'"}


@router.get("/api/products/with-offers", response_model=List[int], dependencies=[Depends(verify_device)])
def get_products_with_offers():
    with SessionCloud() as db:
        product_ids = (
            db.query(OfferModel.product_id)
            .filter(OfferModel.product_id.isnot(None), OfferModel.is_available == True)
            .distinct()
            .all()
        )
        return [p[0] for p in product_ids]


@router.get("/api/products/{product_id}/offers", response_model=List[ProductOfferOutput], dependencies=[Depends(verify_device)])
def get_product_offers(product_id: int):
    with SessionCloud() as db:
        all_offers = (
            db.query(OfferModel)
            .filter(OfferModel.product_id == product_id, OfferModel.is_available == True)
            .order_by(desc(OfferModel.last_seen))
            .all()
        )

        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == 1).first()
        if user:
            user_location = user.location

        rules_map = LogisticsService.get_cached_rules_map()

        best_by_shop = {}
        for o in all_offers:
            canonical_shop = LogisticsService.normalize_shop_name(o.shop_name)
            landing_p = LogisticsService.optimized_get_landing_price(o.price, o.shop_name, user_location, rules_map)
            offer_data = {
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

            if canonical_shop not in best_by_shop:
                best_by_shop[canonical_shop] = offer_data
            else:
                if landing_p < best_by_shop[canonical_shop]["landing_price"]:
                    best_by_shop[canonical_shop] = offer_data

        results = list(best_by_shop.values())
        if results:
            results.sort(key=lambda x: x["landing_price"])
            results[0]["is_best"] = True

        return results


@router.get("/api/market/analytics/{product_id}", response_model=MarketAnalyticsOutput)
def get_market_analytics(product_id: int):
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


@router.get("/api/products/{product_id}/price-history", response_model=List[ProductPriceHistoryOutput])
def get_product_price_history(product_id: int):
    from src.domain.models import PriceHistoryModel, ProductMonthlyStatsModel

    with SessionCloud() as db:
        offers = db.query(OfferModel).filter(OfferModel.product_id == product_id).all()

        shop_groups = defaultdict(list)
        granular_months_by_source = defaultdict(set)
        if offers:
            offer_by_id = {o.id: o for o in offers}
            history_rows = (
                db.query(PriceHistoryModel)
                .filter(PriceHistoryModel.offer_id.in_(list(offer_by_id.keys())))
                .order_by(PriceHistoryModel.recorded_at.asc())
                .all()
            )
            for h in history_rows:
                offer = offer_by_id.get(h.offer_id)
                if not offer:
                    continue
                date_key = h.recorded_at.date().isoformat()
                granular_months_by_source[offer.source_type or "Retail"].add((h.recorded_at.year, h.recorded_at.month))
                shop_groups[offer.shop_name].append({
                    "date": date_key,
                    "price": h.price,
                    "timestamp": h.recorded_at,
                })

        # Incorporar estadísticas mensuales compactadas (> 6 meses) para no perder histórico antiguo
        monthly_stats = (
            db.query(ProductMonthlyStatsModel)
            .filter(ProductMonthlyStatsModel.product_id == product_id)
            .order_by(ProductMonthlyStatsModel.year.asc(), ProductMonthlyStatsModel.month.asc())
            .all()
        )
        for ms in monthly_stats:
            if not ms.year or not ms.month:
                continue
            src = ms.source_type or "Retail"
            ym = (int(ms.year), int(ms.month))
            if ym not in granular_months_by_source[src]:
                rep_price = float(ms.median_price or ms.avg_price or 0.0)
                if rep_price > 0:
                    dt_point = datetime(ym[0], ym[1], 1)
                    shop_label = f"Histórico Mensual ({src})"
                    shop_groups[shop_label].append({
                        "date": dt_point.date().isoformat(),
                        "price": round(rep_price, 2),
                        "timestamp": dt_point,
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


@router.get("/api/products/shops", response_model=List[str])
def get_unique_shops():
    with SessionCloud() as db:
        query = select(OfferModel.shop_name).distinct()
        results = db.execute(query).scalars().all()
        shops = sorted(list(set([r for r in results if r])))
        return shops


@router.get("/api/vintage/products", response_model=List[VintageProductListingOutput])
def get_vintage_products():
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


@router.delete("/api/products/{product_id}", response_model=StatusMessageOutput, dependencies=[Depends(verify_api_key)])
def delete_product(product_id: int):
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

        # 6b. Borrar lore por ítem vinculado a este product_id
        db.query(ProductLoreModel).filter(ProductLoreModel.product_id == product.id).delete()
        
        # 7. Eliminar el producto genérico por completo de la base de datos
        db.delete(product)
        
        db.commit()
        return {
            "status": "success", 
            "message": f"Producto '{product_name}' eliminado de Eternia con éxito. {len(offers)} ofertas devueltas al Purgatorio."
        }


@router.get("/api/vintage/miscellaneous", response_model=List[VintageMiscellaneousItemOutput])
def get_vintage_miscellaneous():
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


@router.post("/api/products/{identifier}/refresh-image", dependencies=[Depends(verify_device)])
def refresh_product_image(identifier: str):
    """
    Descarga la imagen actualizada de una figura desde ActionFigure411 (por ID de figura o producto)
    y la sincroniza en Supabase Storage y Base de Datos.
    """
    from src.application.services.catalog_refresh_service import CatalogRefreshService
    with SessionCloud() as db:
        res = CatalogRefreshService.refresh_figure_image(db, identifier)
        if not res.get("success"):
            raise HTTPException(status_code=400, detail=res.get("error", "Error actualizando imagen"))
        return res
