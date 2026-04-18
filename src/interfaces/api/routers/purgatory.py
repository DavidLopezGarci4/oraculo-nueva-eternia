import json
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError

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

    with SessionCloud() as db:
        offset = (page - 1) * limit
        pending = (
            db.query(PendingMatchModel)
            .order_by(desc(PendingMatchModel.found_at))
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


@router.post("/api/purgatory/match", dependencies=[Depends(verify_api_key)])
async def match_purgatory(request: PurgatoryMatchRequest):
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

        try:
            from src.infrastructure.repositories.product import ProductRepository

            repo = ProductRepository(db)

            user_location = "ES"
            user = db.query(UserModel).filter(UserModel.id == 1).first()
            if user:
                user_location = user.location

            landed_p = LogisticsService.get_landing_price(item.price, item.shop_name, user_location)
            is_wish = any(ci.owner_id == 1 and not ci.acquired for ci in product.collection_items)
            fresh_score = DealScorer.calculate_score(product, landed_p, is_wish)

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
                "last_price_update": datetime.utcnow(),
            }

            new_offer, _ = repo.add_offer(product, offer_data, commit=False)

            history = OfferHistoryModel(
                offer_url=item.url,
                product_name=product.name,
                shop_name=item.shop_name,
                price=item.price,
                action_type="LINKED_MANUAL",
                details=json.dumps({"product_id": product.id, "receipt_id": item.receipt_id}),
            )
            db.add(history)

            db.query(ProductAliasModel).filter(ProductAliasModel.source_url == item.url).delete()
            new_alias = ProductAliasModel(product_id=product.id, source_url=item.url, confirmed=True)
            db.add(new_alias)

            db.delete(item)
            db.commit()
            return {"status": "success", "message": "Vínculo sagrado establecido para la posteridad"}

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error de integridad en match_purgatory: {e}")
            raise HTTPException(status_code=409, detail="Error de integridad: Posible duplicidad de URL o Producto")
        except Exception as e:
            db.rollback()
            logger.error(f"Error inesperado en match_purgatory: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/purgatory/discard", dependencies=[Depends(verify_api_key)])
async def discard_purgatory(request: PurgatoryDiscardRequest):
    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == request.pending_id).first()

        if not item:
            return {"status": "success", "message": "Reliquia ya procesada o inexistente (Idempotencia)"}

        try:
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

            exists = db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url == item.url).first()
            if not exists:
                bl = BlackcludedItemModel(
                    url=item.url,
                    scraped_name=item.scraped_name,
                    reason=request.reason,
                    source_type=item.source_type,
                )
                db.add(bl)

            history = OfferHistoryModel(
                offer_url=item.url,
                product_name=item.scraped_name,
                shop_name=item.shop_name,
                price=item.price,
                action_type="DISCARDED_MANUAL",
                details=json.dumps({"reason": request.reason, "original_item": item_data}),
            )
            db.add(history)

            db.delete(item)
            db.commit()
            return {"status": "success", "message": "Item enviado a las sombras de la lista negra"}

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error de integridad en discard_purgatory: {e}")
            db.delete(item)
            db.commit()
            return {"status": "success", "message": "Item ya estaba en lista negra, purificado del Purgatorio"}
        except Exception as e:
            db.rollback()
            logger.error(f"Error inesperado en discard_purgatory: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/purgatory/discard/bulk", dependencies=[Depends(verify_api_key)])
async def discard_purgatory_bulk(request: PurgatoryBulkDiscardRequest):
    with SessionCloud() as db:
        items = db.query(PendingMatchModel).filter(PendingMatchModel.id.in_(request.pending_ids)).all()
        count = 0
        for item in items:
            exists = db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url == item.url).first()
            if not exists:
                blacklist = BlackcludedItemModel(
                    url=item.url,
                    scraped_name=item.scraped_name,
                    reason=request.reason,
                )
                db.add(blacklist)

            history = OfferHistoryModel(
                offer_url=item.url,
                product_name=item.scraped_name,
                shop_name=item.shop_name,
                price=item.price,
                action_type="DISCARDED_BULK",
                details=json.dumps({"reason": request.reason}),
            )
            db.add(history)

            db.delete(item)
            count += 1

        db.commit()

    return {"status": "success", "message": f"{count} items desterrados al abismo."}


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
