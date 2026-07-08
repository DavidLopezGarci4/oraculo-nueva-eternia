import json
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from loguru import logger
from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Optional

PROCESSING_IDS = set()

class VintageMatchRequest(BaseModel):
    custom_name: Optional[str] = None
    product_id: Optional[int] = None
    is_vintage: Optional[bool] = True
    sub_category: Optional[str] = None


from src.application.services.deal_scorer import DealScorer
from src.application.services.logistics_service import LogisticsService
from src.domain.models import (
    BlackcludedItemModel,
    OfferHistoryModel,
    OfferModel,
    PendingMatchModel,
    ProductAliasModel,
    ProductModel,
    UserModel,
)
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_api_key
from src.interfaces.api.schemas import (
    PurgatoryBulkDiscardRequest,
    PurgatoryDiscardRequest,
    PurgatoryMatchRequest,
    PurgatoryBulkMatchRequest,
    RelinkOfferRequest,
)

router = APIRouter(tags=["purgatory"])


_STOP_WORDS = {"masters", "of", "the", "universe", "origins", "motu"}


def _build_product_index(products: list) -> tuple[dict, dict]:
    """
    Builds two lookup structures from the product list (called once per request):
      token_index : token → [ProductModel, ...]  — for name-based pre-filtering
      ean_index   : ean   → [ProductModel, ...]  — for exact EAN matches

    Reduces the matching loop from O(pending × all_products) to
    O(pending × avg_candidates), typically a 10-50x speedup.
    """
    token_index: dict = {}
    ean_index: dict = {}
    for p in products:
        for token in set(re.findall(r"\w+", (p.name or "").lower())) - _STOP_WORDS:
            token_index.setdefault(token, []).append(p)
        if p.ean:
            ean_index.setdefault(p.ean, []).append(p)
    return token_index, ean_index


@router.get("/api/purgatory", dependencies=[Depends(verify_api_key)])
async def get_purgatory(page: int = 1, limit: int = 500):
    from src.core.brain_engine import engine
    from src.infrastructure.scrapers.pipeline import clean_purgatory_globally

    with SessionCloud() as db:
        # Limpieza global proactiva del purgatorio
        clean_purgatory_globally(db)
        db.commit()
        
        offset = (page - 1) * limit
        query = db.query(PendingMatchModel)
        if PROCESSING_IDS:
            query = query.filter(~PendingMatchModel.id.in_(list(PROCESSING_IDS)))
            
        pending = (
            query.order_by(desc(PendingMatchModel.found_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Single DB round-trip; index built once for the whole page
        products = db.query(ProductModel).all()
        token_index, ean_index = _build_product_index(products)

        results = []
        for item in pending:
            try:
                scraped_name_safe = (item.scraped_name or "").lower()
                search_tokens = set(re.findall(r"\w+", scraped_name_safe)) - _STOP_WORDS

                # Gather candidates via index — avoids iterating over every product
                candidates: set = set()
                for token in search_tokens:
                    candidates.update(token_index.get(token, []))
                if item.ean:
                    candidates.update(ean_index.get(item.ean, []))

                suggestions = []
                for p in candidates:
                    _, score, reason = engine.calculate_match(p.name, item.scraped_name, p.ean, item.ean)
                    if score > 0.30:
                        suggestions.append({
                            "product_id": p.id,
                            "name": p.name,
                            "figure_id": p.figure_id,
                            "sub_category": p.sub_category,
                            "is_vintage": p.is_vintage,
                            "release_year": p.release_year,
                            "variant_name": p.variant_name,
                            "match_score": round(score * 100, 1),
                            "reason": reason,
                        })

                suggestions.sort(key=lambda x: x["match_score"], reverse=True)

                results.append({
                    "id": item.id,
                    "scraped_name": item.scraped_name,
                    "ean": item.ean,
                    "price": item.price,
                    "currency": item.currency,
                    "url": item.url,
                    "shop_name": item.shop_name,
                    "image_url": item.image_url,
                    "found_at": item.found_at,
                    "source_type": item.source_type,
                    "validation_status": item.validation_status,
                    "is_blocked": item.is_blocked,
                    "opportunity_score": item.opportunity_score,
                    "anomaly_flags": json.loads(item.anomaly_flags) if item.anomaly_flags else [],
                    "suggestions": suggestions[:5],
                })
            except Exception as e:
                logger.error(f"Error procesando item {getattr(item, 'id', 'unknown')} en Purgatorio: {e}")
                continue

        return results


def run_match_task(pending_id: int, product_id: int):
    try:
        with SessionCloud() as db:
            item = db.query(PendingMatchModel).filter(PendingMatchModel.id == pending_id).first()
            product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
            if not item or not product:
                return

            from src.infrastructure.repositories.product import ProductRepository
            repo = ProductRepository(db)

            user_location = "ES"
            user = db.query(UserModel).filter(UserModel.id == 1).first()
            if user:
                user_location = user.location

            landed_p = LogisticsService.get_landing_price(item.price, item.shop_name, user_location)
            is_wish = any(ci.owner_id == 1 and not ci.acquired for ci in product.collection_items)
            fresh_score = DealScorer.calculate_score(product, landed_p, is_wish)

            is_v = bool(product.is_vintage)
            if is_v:
                from src.domain.models import VintageProductModel
                exists_v = db.query(VintageProductModel).filter(VintageProductModel.product_id == product.id).first()
                if not exists_v:
                    v_prod = VintageProductModel(product_id=product.id, notes="Auto-detectado vintage al vincular en Purgatorio")
                    db.add(v_prod)

            offer_data = {
                "shop_name": item.shop_name,
                "price": item.price,
                "currency": item.currency,
                "url": item.url,
                "is_available": True,
                "source_type": item.source_type,
                "receipt_id": item.receipt_id,
                "opportunity_score": fresh_score,
                "first_seen_at": item.found_at,
                "last_price_update": datetime.now(timezone.utc),
                "is_vintage": is_v,
                "condition": item.condition or "Loose",
                "grading": item.grading or 7.5,
            }

            new_offer, _ = repo.add_offer(product, offer_data, commit=False)

            history = OfferHistoryModel(
                offer_url=item.url,
                product_name=product.name,
                shop_name=item.shop_name,
                price=item.price,
                action_type="LINKED_MANUAL",
                details=json.dumps({"product_id": product.id, "receipt_id": item.receipt_id, "is_vintage": is_v}),
            )
            db.add(history)

            db.query(ProductAliasModel).filter(ProductAliasModel.source_url == item.url).delete()
            new_alias = ProductAliasModel(product_id=product.id, source_url=item.url, confirmed=True)
            db.add(new_alias)

            db.delete(item)
            db.commit()
    except Exception as e:
        logger.error(f"Error inesperado en background match_purgatory para item {pending_id}: {e}")
    finally:
        PROCESSING_IDS.discard(pending_id)


@router.post("/api/purgatory/match", dependencies=[Depends(verify_api_key)])
async def match_purgatory(request: PurgatoryMatchRequest, background_tasks: BackgroundTasks):
    if request.pending_id in PROCESSING_IDS:
        return {"status": "success", "message": "Vinculación ya se está procesando en segundo plano"}

    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == request.pending_id).first()
        product = db.query(ProductModel).filter(ProductModel.id == request.product_id).first()

        if not item:
            existing_offer = db.query(OfferModel).filter(OfferModel.product_id == request.product_id).first()
            if existing_offer:
                return {"status": "success", "message": "Reliquia ya procesada previamente (Idempotencia)"}
            raise HTTPException(status_code=404, detail="Reliquia no encontrada en el Purgatorio")

        if not product:
            raise HTTPException(status_code=404, detail="Producto objetivo no encontrado")

    PROCESSING_IDS.add(request.pending_id)
    background_tasks.add_task(run_match_task, request.pending_id, request.product_id)
    return {"status": "success", "message": "Vinculación programada en segundo plano"}


def run_match_bulk_task(matches: list[dict]):
    from src.infrastructure.repositories.product import ProductRepository
    
    with SessionCloud() as db:
        repo = ProductRepository(db)
        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == 1).first()
        if user:
            user_location = user.location
            
        for m in matches:
            pending_id = m["pending_id"]
            product_id = m["product_id"]
            
            try:
                with db.begin_nested():
                    item = db.query(PendingMatchModel).filter(PendingMatchModel.id == pending_id).first()
                    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
                    
                    if not item:
                        existing_offer = db.query(OfferModel).filter(OfferModel.product_id == product_id).first()
                        if existing_offer:
                            logger.info(f"Bulk match item {pending_id} already matched previously.")
                            continue
                        raise ValueError(f"Reliquia {pending_id} no encontrada.")
                        
                    if not product:
                        raise ValueError(f"Producto {product_id} no encontrado.")
                        
                    landed_p = LogisticsService.get_landing_price(item.price, item.shop_name, user_location)
                    is_wish = any(ci.owner_id == 1 and not ci.acquired for ci in product.collection_items)
                    fresh_score = DealScorer.calculate_score(product, landed_p, is_wish)
                    
                    is_v = bool(product.is_vintage)
                    if is_v:
                        from src.domain.models import VintageProductModel
                        exists_v = db.query(VintageProductModel).filter(VintageProductModel.product_id == product.id).first()
                        if not exists_v:
                            v_prod = VintageProductModel(product_id=product.id, notes="Auto-detectado vintage al vincular (Bulk)")
                            db.add(v_prod)
                            
                    offer_data = {
                        "shop_name": item.shop_name,
                        "price": item.price,
                        "currency": item.currency,
                        "url": item.url,
                        "is_available": True,
                        "source_type": item.source_type,
                        "receipt_id": item.receipt_id,
                        "opportunity_score": fresh_score,
                        "first_seen_at": item.found_at,
                        "last_price_update": datetime.now(timezone.utc),
                        "is_vintage": is_v,
                        "condition": item.condition or "Loose",
                        "grading": item.grading or 7.5,
                    }
                    
                    repo.add_offer(product, offer_data, commit=False)
                    
                    history = OfferHistoryModel(
                        offer_url=item.url,
                        product_name=product.name,
                        shop_name=item.shop_name,
                        price=item.price,
                        action_type="LINKED_MANUAL_BULK",
                        details=json.dumps({"product_id": product.id, "receipt_id": item.receipt_id, "is_vintage": is_v}),
                    )
                    db.add(history)
                    
                    db.query(ProductAliasModel).filter(ProductAliasModel.source_url == item.url).delete()
                    db.add(ProductAliasModel(product_id=product.id, source_url=item.url, confirmed=True))
                    
                    db.delete(item)
                logger.info(f"Bulk match item {pending_id} staged successfully.")
            except Exception as e:
                logger.error(f"Error procesando bulk match item {pending_id} -> producto {product_id}: {e}")
            finally:
                PROCESSING_IDS.discard(pending_id)
                
        try:
            db.commit()
            logger.info("Committed successful bulk matches.")
        except Exception as e:
            db.rollback()
            logger.error(f"Fallo crítico al hacer commit del lote bulk match: {e}")


@router.post("/api/purgatory/match/bulk", dependencies=[Depends(verify_api_key)])
async def match_purgatory_bulk(request: PurgatoryBulkMatchRequest, background_tasks: BackgroundTasks):
    to_process = []
    for m in request.matches:
        if m.pending_id not in PROCESSING_IDS:
            PROCESSING_IDS.add(m.pending_id)
            to_process.append({"pending_id": m.pending_id, "product_id": m.product_id})
            
    if not to_process:
        return {"status": "success", "message": "Todas las vinculaciones ya se están procesando"}
        
    background_tasks.add_task(run_match_bulk_task, to_process)
    return {"status": "success", "message": f"{len(to_process)} vinculaciones programadas en segundo plano"}


def run_discard_task(pending_id: int, reason: str):
    try:
        with SessionCloud() as db:
            item = db.query(PendingMatchModel).filter(PendingMatchModel.id == pending_id).first()
            if not item:
                return

            item_data = {
                "scraped_name": item.scraped_name,
                "ean": item.ean,
                "price": item.price,
                "currency": item.currency,
                "url": item.url,
                "shop_name": item.shop_name,
                "image_url": item.image_url,
                "receipt_id": item.receipt_id,
            }

            from src.core.url_utils import normalize_url
            normalized_url = normalize_url(item.url)

            exists = db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url == normalized_url).first()
            if not exists:
                bl = BlackcludedItemModel(
                    url=normalized_url,
                    scraped_name=item.scraped_name,
                    reason=reason,
                    source_type=item.source_type,
                )
                db.add(bl)

            history = OfferHistoryModel(
                offer_url=item.url,
                product_name=item.scraped_name,
                shop_name=item.shop_name,
                price=item.price,
                action_type="DISCARDED_MANUAL",
                details=json.dumps({"reason": reason, "original_item": item_data}),
            )
            db.add(history)

            db.delete(item)
            db.commit()
    except IntegrityError as e:
        db.rollback()
        # Idempotent cleanup if it already exists in blacklist
        try:
            with SessionCloud() as db2:
                item2 = db2.query(PendingMatchModel).filter(PendingMatchModel.id == pending_id).first()
                if item2:
                    db2.delete(item2)
                    db2.commit()
        except:
            pass
    except Exception as e:
        logger.error(f"Error inesperado en background discard_purgatory para item {pending_id}: {e}")
    finally:
        PROCESSING_IDS.discard(pending_id)


@router.post("/api/purgatory/discard", dependencies=[Depends(verify_api_key)])
async def discard_purgatory(request: PurgatoryDiscardRequest, background_tasks: BackgroundTasks):
    if request.pending_id in PROCESSING_IDS:
        return {"status": "success", "message": "El descarte ya se está procesando en segundo plano"}

    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == request.pending_id).first()
        if not item:
            return {"status": "success", "message": "Reliquia ya procesada o inexistente (Idempotencia)"}

    PROCESSING_IDS.add(request.pending_id)
    background_tasks.add_task(run_discard_task, request.pending_id, request.reason)
    return {"status": "success", "message": "Descarte programado en segundo plano"}


def run_discard_bulk_task(pending_ids: list[int], reason: str):
    try:
        with SessionCloud() as db:
            items = db.query(PendingMatchModel).filter(PendingMatchModel.id.in_(pending_ids)).all()
            from src.core.url_utils import normalize_url
            for item in items:
                normalized_url = normalize_url(item.url)
                exists = db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url == normalized_url).first()
                if not exists:
                    blacklist = BlackcludedItemModel(
                        url=normalized_url,
                        scraped_name=item.scraped_name,
                        reason=reason,
                    )
                    blacklist_ref = db.add(blacklist)

                history = OfferHistoryModel(
                    offer_url=item.url,
                    product_name=item.scraped_name,
                    shop_name=item.shop_name,
                    price=item.price,
                    action_type="DISCARDED_BULK",
                    details=json.dumps({"reason": reason}),
                )
                db.add(history)

                db.delete(item)
            db.commit()
    except Exception as e:
        logger.error(f"Error inesperado en background discard_purgatory_bulk: {e}")
    finally:
        for pid in pending_ids:
            PROCESSING_IDS.discard(pid)


@router.post("/api/purgatory/discard/bulk", dependencies=[Depends(verify_api_key)])
async def discard_purgatory_bulk(request: PurgatoryBulkDiscardRequest, background_tasks: BackgroundTasks):
    to_process = [pid for pid in request.pending_ids if pid not in PROCESSING_IDS]
    if not to_process:
        return {"status": "success", "message": "Todos los descartes ya se están procesando"}

    for pid in to_process:
        PROCESSING_IDS.add(pid)

    background_tasks.add_task(run_discard_bulk_task, to_process, request.reason)
    return {"status": "success", "message": f"Descarte en lote de {len(to_process)} items programado en segundo plano"}


@router.post("/api/offers/{offer_id}/unlink", dependencies=[Depends(verify_api_key)])
async def unlink_offer(offer_id: int):
    with SessionCloud() as db:
        offer = db.query(OfferModel).filter(OfferModel.id == offer_id).first()
        if not offer:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        product_name = offer.product.name if offer.product else "Reliquia Desconocida"

        purgatory_item = PendingMatchModel(
            scraped_name=product_name,
            ean=None,
            price=offer.price,
            currency=offer.currency,
            url=offer.url,
            shop_name=offer.shop_name,
            image_url=None,
            source_type=offer.source_type,
        )
        db.add(purgatory_item)

        history = OfferHistoryModel(
            offer_url=offer.url,
            product_name=product_name,
            shop_name=offer.shop_name,
            price=offer.price,
            action_type="UNLINKED_MANUAL_ADMIN",
            details=json.dumps({"reason": "Desvinculación manual por el Arquitecto"}),
        )
        db.add(history)

        db.query(ProductAliasModel).filter(ProductAliasModel.source_url == offer.url).delete()
        db.delete(offer)
        db.commit()
        return {"status": "success", "message": f"Justicia del Arquitecto: '{product_name}' ha sido devuelto al Purgatorio"}


@router.post("/api/offers/{offer_id}/relink", dependencies=[Depends(verify_api_key)])
async def relink_offer(offer_id: int, request: RelinkOfferRequest):
    with SessionCloud() as db:
        offer = db.query(OfferModel).filter(OfferModel.id == offer_id).first()
        if not offer:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        old_product_name = offer.product.name if offer.product else "Desconocido"
        new_product = db.query(ProductModel).filter(ProductModel.id == request.target_product_id).first()
        if not new_product:
            raise HTTPException(status_code=404, detail="Producto destino no encontrado")

        offer.product_id = new_product.id

        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == 1).first()
        if user:
            user_location = user.location

        landed_p = LogisticsService.get_landing_price(offer.price, offer.shop_name, user_location)
        is_wish = any(ci.owner_id == 1 and not ci.acquired for ci in new_product.collection_items)
        offer.opportunity_score = DealScorer.calculate_score(new_product, landed_p, is_wish)

        db.query(ProductAliasModel).filter(ProductAliasModel.source_url == offer.url).delete()
        new_alias = ProductAliasModel(product_id=new_product.id, source_url=offer.url, confirmed=True)
        db.add(new_alias)

        history = OfferHistoryModel(
            offer_url=offer.url,
            product_name=new_product.name,
            shop_name=offer.shop_name,
            price=offer.price,
            action_type="RELINKED_MANUAL_ADMIN",
            details=json.dumps({
                "from_product": old_product_name,
                "to_product": new_product.name,
                "reason": "Redirección manual por el Arquitecto",
            }),
        )
        db.add(history)

        db.commit()
        return {"status": "success", "message": f"Decreto del Arquitecto: Oferta reasignada a '{new_product.name}'"}


def run_match_vintage_task(pending_id: int, custom_name: Optional[str], product_id: Optional[int], is_vintage: bool = True, sub_category: Optional[str] = None):
    try:
        with SessionCloud() as db:
            item = db.query(PendingMatchModel).filter(PendingMatchModel.id == pending_id).first()
            if not item:
                return

            product = None
            if product_id:
                product = db.query(ProductModel).filter(ProductModel.id == product_id).first()

            if not product and custom_name:
                clean_name = custom_name.strip()
                if is_vintage:
                    if not clean_name.lower().endswith(" vintage"):
                        clean_name = f"{clean_name} Vintage"

                    product = db.query(ProductModel).filter(
                        func.lower(ProductModel.name) == func.lower(clean_name),
                        ProductModel.is_vintage == True
                    ).first()
                else:
                    product = db.query(ProductModel).filter(
                        func.lower(ProductModel.name) == func.lower(clean_name),
                        ProductModel.is_vintage.is_not(True)
                    ).first()

                if not product:
                    import random
                    if is_vintage:
                        rand_id = f"VINT-{random.randint(1000, 9999)}"
                        product = ProductModel(
                            name=clean_name,
                            ean=item.ean,
                            image_url=item.image_url,
                            category="Masters of the Universe",
                            sub_category="Vintage",
                            is_vintage=True,
                            figure_id=rand_id
                        )
                    else:
                        rand_id = f"ORIG-{random.randint(1000, 9999)}"
                        product = ProductModel(
                            name=clean_name,
                            ean=item.ean,
                            image_url=item.image_url,
                            category="Masters of the Universe",
                            sub_category=sub_category or "Origins",
                            is_vintage=False,
                            figure_id=rand_id
                        )
                    db.add(product)
                    db.flush()

            # Fallback
            if not product:
                clean_scraped = item.scraped_name.strip()
                if is_vintage:
                    if not clean_scraped.lower().endswith(" vintage"):
                        clean_scraped = f"{clean_scraped} Vintage"

                    product = db.query(ProductModel).filter(
                        func.lower(ProductModel.name) == func.lower(clean_scraped),
                        ProductModel.is_vintage == True
                    ).first()
                else:
                    product = db.query(ProductModel).filter(
                        func.lower(ProductModel.name) == func.lower(clean_scraped),
                        ProductModel.is_vintage.is_not(True)
                    ).first()

                if not product:
                    import random
                    if is_vintage:
                        rand_id = f"VINT-{random.randint(1000, 9999)}"
                        product = ProductModel(
                            name=clean_scraped,
                            ean=item.ean,
                            image_url=item.image_url,
                            category="Masters of the Universe",
                            sub_category="Vintage",
                            is_vintage=True,
                            figure_id=rand_id
                        )
                    else:
                        rand_id = f"ORIG-{random.randint(1000, 9999)}"
                        product = ProductModel(
                            name=clean_scraped,
                            ean=item.ean,
                            image_url=item.image_url,
                            category="Masters of the Universe",
                            sub_category=sub_category or "Origins",
                            is_vintage=False,
                            figure_id=rand_id
                        )
                    db.add(product)
                    db.flush()
            else:
                if is_vintage:
                    product.is_vintage = True

            if is_vintage:
                # Register in the vintage_products table
                from src.domain.models import VintageProductModel
                exists_v = db.query(VintageProductModel).filter(VintageProductModel.product_id == product.id).first()
                if not exists_v:
                    v_prod = VintageProductModel(
                        product_id=product.id,
                        notes=f"Clasificado manualmente como Vintage desde Purgatorio para {item.shop_name}"
                    )
                    db.add(v_prod)

            # Create individual offer marked as vintage
            from src.infrastructure.repositories.product import ProductRepository
            repo = ProductRepository(db)

            user_location = "ES"
            user = db.query(UserModel).filter(UserModel.id == 1).first()
            if user:
                user_location = user.location

            landed_p = LogisticsService.get_landing_price(item.price, item.shop_name, user_location)
            is_wish = any(ci.owner_id == 1 and not ci.acquired for ci in product.collection_items)
            fresh_score = DealScorer.calculate_score(product, landed_p, is_wish)

            # Detect condition and grading from scraped name if not present
            cond = item.condition or ("MOC" if "moc" in item.scraped_name.lower() or "caja" in item.scraped_name.lower() or "nuevo" in item.scraped_name.lower() else "Loose")
            grad = item.grading or (9.0 if cond == "MOC" else 7.5)

            offer_data = {
                "shop_name": item.shop_name,
                "price": item.price,
                "currency": item.currency,
                "url": item.url,
                "is_available": True,
                "source_type": item.source_type,
                "receipt_id": item.receipt_id,
                "opportunity_score": fresh_score,
                "first_seen_at": item.found_at,
                "last_price_update": datetime.now(timezone.utc),
                "is_vintage": is_vintage,
                "condition": cond,
                "grading": grad,
                "image_url": item.image_url,
            }

            new_offer, _ = repo.add_offer(product, offer_data, commit=False)

            # Audit Trail
            from src.domain.models import OfferHistoryModel
            history = OfferHistoryModel(
                offer_url=item.url,
                product_name=product.name,
                shop_name=item.shop_name,
                price=item.price,
                action_type="LINKED_VINTAGE" if is_vintage else "LINKED_MANUAL",
                details=json.dumps({"product_id": product.id, "receipt_id": item.receipt_id, "condition": cond, "grading": grad}),
            )
            db.add(history)

            # Create alias
            db.query(ProductAliasModel).filter(ProductAliasModel.source_url == item.url).delete()
            new_alias = ProductAliasModel(product_id=product.id, source_url=item.url, confirmed=True)
            db.add(new_alias)

            db.delete(item)
            db.commit()
    except Exception as e:
        logger.error(f"Error en background match_purgatory_vintage para item {pending_id}: {e}")
    finally:
        PROCESSING_IDS.discard(pending_id)


@router.post("/api/purgatory/{pending_id}/vintage", dependencies=[Depends(verify_api_key)])
async def match_purgatory_vintage(pending_id: int, background_tasks: BackgroundTasks, request: Optional[VintageMatchRequest] = None):
    if pending_id in PROCESSING_IDS:
        return {"status": "success", "message": "La clasificación ya se está procesando en segundo plano"}

    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == pending_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Reliquia no encontrada en el Purgatorio")

    custom_name = request.custom_name if request else None
    product_id = request.product_id if request else None
    is_vintage = request.is_vintage if (request and request.is_vintage is not None) else True
    sub_category = request.sub_category if request else None

    PROCESSING_IDS.add(pending_id)
    background_tasks.add_task(run_match_vintage_task, pending_id, custom_name, product_id, is_vintage, sub_category)
    return {"status": "success", "message": "Clasificación programada en segundo plano."}


@router.post("/api/vintage/revert-offer/{offer_id}", dependencies=[Depends(verify_api_key)])
async def revert_vintage_offer(offer_id: int):
    with SessionCloud() as db:
        offer = db.query(OfferModel).filter(OfferModel.id == offer_id).first()
        if not offer:
            raise HTTPException(status_code=404, detail="Oferta Vintage no encontrada")

        product = offer.product
        try:
            # Recreate pending match
            purgatory_item = PendingMatchModel(
                scraped_name=product.name if product else "Reliquia Vintage Revertida",
                ean=product.ean if product else None,
                price=offer.price,
                currency=offer.currency,
                url=offer.url,
                shop_name=offer.shop_name,
                image_url=offer.image_url or (product.image_url if product else None),
                source_type=offer.source_type,
                condition=offer.condition or "Loose",
                grading=offer.grading or 7.5,
                is_vintage=True
            )
            db.add(purgatory_item)

            # Add History
            from src.domain.models import OfferHistoryModel
            history = OfferHistoryModel(
                offer_url=offer.url,
                product_name=product.name if product else "Reliquia Vintage",
                shop_name=offer.shop_name,
                price=offer.price,
                action_type="REVERTED_VINTAGE",
                details=json.dumps({"reason": "Reversión manual desde Pabellón Vintage", "offer_id": offer.id}),
            )
            db.add(history)

            # Unlink alias
            db.query(ProductAliasModel).filter(ProductAliasModel.source_url == offer.url).delete()

            # Delete the individual offer
            db.delete(offer)
            
            # Check if there are any remaining vintage offers for this product. If not, clear its is_vintage flag.
            db.flush()
            remaining_v_offers = db.query(OfferModel).filter(
                OfferModel.product_id == product.id,
                OfferModel.is_vintage == True
            ).count()
            if remaining_v_offers == 0:
                product.is_vintage = False
                from src.domain.models import VintageProductModel
                db.query(VintageProductModel).filter(VintageProductModel.product_id == product.id).delete()

            db.commit()
            return {"status": "success", "message": "Oferta desclasificada de Vintage y devuelta al Purgatorio"}

        except Exception as e:
            db.rollback()
            logger.error(f"Error al revertir oferta vintage: {e}")
            raise HTTPException(status_code=500, detail=str(e))


def run_match_miscellaneous_task(pending_id: int):
    try:
        with SessionCloud() as db:
            item = db.query(PendingMatchModel).filter(PendingMatchModel.id == pending_id).first()
            if not item:
                return

            from src.domain.models import VintageMiscellaneousModel
            from src.core.url_utils import normalize_url
            normalized_url = normalize_url(item.url)

            misc_item = VintageMiscellaneousModel(
                title=item.scraped_name,
                url=normalized_url,
                price=item.price,
                currency=item.currency,
                shop_name=item.shop_name,
                image_url=item.image_url,
                condition=item.condition or "Loose",
                grading=item.grading or 7.5,
                notes=f"Clasificado como Lote/Miscelánea Vintage desde Purgatorio para {item.shop_name}"
            )
            db.add(misc_item)

            from src.domain.models import OfferHistoryModel
            history = OfferHistoryModel(
                offer_url=normalized_url,
                product_name=item.scraped_name,
                shop_name=item.shop_name,
                price=item.price,
                action_type="LINKED_MISCELLANEOUS",
                details=json.dumps({"receipt_id": item.receipt_id, "shop_name": item.shop_name}),
            )
            db.add(history)

            db.delete(item)
            db.commit()
    except IntegrityError as e:
        db.rollback()
        # Deduplicate: if it already existed in miscellaneous, just delete the pending match to keep it clean
        try:
            with SessionCloud() as db2:
                item2 = db2.query(PendingMatchModel).filter(PendingMatchModel.id == pending_id).first()
                if item2:
                    db2.delete(item2)
                    db2.commit()
        except:
            pass
    except Exception as e:
        logger.error(f"Error en background match_purgatory_miscellaneous para item {pending_id}: {e}")
    finally:
        PROCESSING_IDS.discard(pending_id)


@router.post("/api/purgatory/{pending_id}/miscellaneous", dependencies=[Depends(verify_api_key)])
async def match_purgatory_miscellaneous(pending_id: int, background_tasks: BackgroundTasks):
    if pending_id in PROCESSING_IDS:
        return {"status": "success", "message": "La clasificación miscelánea ya se está procesando en segundo plano"}

    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == pending_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Reliquia no encontrada en el Purgatorio")

    PROCESSING_IDS.add(pending_id)
    background_tasks.add_task(run_match_miscellaneous_task, pending_id)
    return {"status": "success", "message": "Clasificación miscelánea programada en segundo plano."}


@router.post("/api/vintage/miscellaneous/revert/{item_id}", dependencies=[Depends(verify_api_key)])
async def revert_miscellaneous_item(item_id: int):
    with SessionCloud() as db:
        from src.domain.models import VintageMiscellaneousModel
        misc_item = db.query(VintageMiscellaneousModel).filter(VintageMiscellaneousModel.id == item_id).first()
        if not misc_item:
            raise HTTPException(status_code=404, detail="Artículo de Miscelánea no encontrado")

        try:
            purgatory_item = PendingMatchModel(
                scraped_name=misc_item.title,
                ean=None,
                price=misc_item.price,
                currency=misc_item.currency,
                url=misc_item.url,
                shop_name=misc_item.shop_name,
                image_url=misc_item.image_url,
                source_type="Peer-to-Peer",
                condition=misc_item.condition or "Loose",
                grading=misc_item.grading or 7.5,
                is_vintage=True
            )
            db.add(purgatory_item)

            from src.domain.models import OfferHistoryModel
            history = OfferHistoryModel(
                offer_url=misc_item.url,
                product_name=misc_item.title,
                shop_name=misc_item.shop_name,
                price=misc_item.price,
                action_type="REVERTED_MISCELLANEOUS",
                details=json.dumps({"reason": "Reversión manual desde Miscelánea Vintage", "item_id": misc_item.id}),
            )
            db.add(history)

            db.delete(misc_item)
            db.commit()
            return {"status": "success", "message": "Artículo devuelto al Purgatorio con éxito."}

        except Exception as e:
            db.rollback()
            logger.error(f"Error al revertir miscelánea vintage: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/vintage/miscellaneous/{item_id}", dependencies=[Depends(verify_api_key)])
async def delete_miscellaneous_item(item_id: int):
    with SessionCloud() as db:
        from src.domain.models import VintageMiscellaneousModel
        misc_item = db.query(VintageMiscellaneousModel).filter(VintageMiscellaneousModel.id == item_id).first()
        if not misc_item:
            raise HTTPException(status_code=404, detail="Artículo de Miscelánea no encontrado")

        try:
            from src.domain.models import OfferHistoryModel
            history = OfferHistoryModel(
                offer_url=misc_item.url,
                product_name=misc_item.title,
                shop_name=misc_item.shop_name,
                price=misc_item.price,
                action_type="DELETED_MISCELLANEOUS",
                details=json.dumps({"reason": "Eliminación manual desde Miscelánea Vintage", "item_id": misc_item.id}),
            )
            db.add(history)

            db.delete(misc_item)
            db.commit()
            return {"status": "success", "message": "Artículo de Miscelánea eliminado con éxito."}

        except Exception as e:
            db.rollback()
            logger.error(f"Error al eliminar artículo de miscelánea: {e}")
            raise HTTPException(status_code=500, detail=str(e))
