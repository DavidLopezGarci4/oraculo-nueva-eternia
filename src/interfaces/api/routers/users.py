import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from src.application.services.logistics_service import LogisticsService
from src.domain.models import OfferModel, PendingMatchModel, ProductModel, UserModel, BlackcludedItemModel, VintageMiscellaneousModel, OfferHistoryModel
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import get_current_user, scope_user_id, verify_device
from src.interfaces.api.schemas import WallapopImportRequest, UserImagePathsUpdateRequest

router = APIRouter(tags=["users"])


@router.get("/api/users/{user_id}", dependencies=[Depends(verify_device)])
async def get_user_settings(user_id: int, current_user: UserModel = Depends(get_current_user)):
    user_id = scope_user_id(current_user, user_id)
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "location": user.location,
            "role": user.role,
            "is_public_showcase": user.is_public_showcase,
            "pc_image_path": user.pc_image_path,
            "mobile_image_path": user.mobile_image_path,
        }


@router.post("/api/users/{user_id}/image-paths")
async def update_user_image_paths(
    user_id: int,
    request: UserImagePathsUpdateRequest,
    current_user: UserModel = Depends(get_current_user),
):
    # Fase AAA-2.1: antes cualquiera (sin auth) podía fijar la ruta de imágenes
    # personalizada de OTRO usuario, con impacto directo en qué ficheros sirve
    # /api/static/images (main.py). Ahora exige sesión y queda limitado a la
    # propia cuenta (salvo admin).
    user_id = scope_user_id(current_user, user_id)
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        user.pc_image_path = request.pc_path
        user.mobile_image_path = request.mobile_path
        db.commit()
        return {
            "status": "success",
            "pc_image_path": user.pc_image_path,
            "mobile_image_path": user.mobile_image_path
        }


@router.post("/api/users/{user_id}/location")
async def update_user_location(
    user_id: int,
    location: str,
    current_user: UserModel = Depends(get_current_user),
):
    user_id = scope_user_id(current_user, user_id)
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        user.location = location.upper()
        db.commit()
        return {"status": "success", "location": user.location}


@router.post("/api/users/{user_id}/public-showcase")
async def update_user_showcase(
    user_id: int,
    is_public: bool,
    current_user: UserModel = Depends(get_current_user),
):
    # Fase AAA-2.1: este era el hallazgo más grave del router — sin auth,
    # cualquiera podía activar el escaparate PÚBLICO de otra persona
    # (/santuario/{username}, sin login) y exponer su colección privada sin
    # consentimiento. Ahora exige sesión y queda limitado a la propia cuenta.
    user_id = scope_user_id(current_user, user_id)
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        user.is_public_showcase = is_public
        db.commit()
        return {"status": "success", "is_public_showcase": user.is_public_showcase}


@router.post("/api/wallapop/import")
async def import_wallapop_products(request: WallapopImportRequest):
    # Nota (Fase AAA-2.1): la extensión de Chrome (chrome-extension/content.js)
    # llama a este endpoint SIN ninguna cabecera de auth. Queda intencionalmente
    # sin proteger por ahora para no romperla; el impacto de un abuso anónimo es
    # bajo (solo encola candidatos en el Purgatorio, que ya está gateado por
    # verify_api_key para su revisión/aprobación). Pendiente: dar a la extensión
    # una API key propia y exigirla aquí (ver reporte, Fase 2 — trabajo futuro).
    imported = 0
    from src.core.url_utils import normalize_url
    from src.core.vintage_utils import validate_motu_relevance
    from src.infrastructure.scrapers.pipeline import clean_purgatory_globally
    
    # Normalize all incoming URLs first
    for p in request.products:
        if p.url:
            p.url = normalize_url(p.url)
            
    with SessionCloud() as db:
        # Global proactive cleanup before processing new ones
        clean_purgatory_globally(db)
        
        urls = [p.url for p in request.products if p.url]
        if not urls:
            return {"status": "success", "imported": 0, "total_received": 0}

        active_urls = set(
            x[0] for x in db.query(OfferModel.url).filter(OfferModel.url.in_(urls)).all()
        )
        blocked_urls = set(
            x[0] for x in db.query(BlackcludedItemModel.url).filter(BlackcludedItemModel.url.in_(urls)).all()
        )
        misc_urls = set(
            x[0] for x in db.query(VintageMiscellaneousModel.url).filter(VintageMiscellaneousModel.url.in_(urls)).all()
        )
        purgatory_urls = set(
            x[0] for x in db.query(PendingMatchModel.url).filter(PendingMatchModel.url.in_(urls)).all()
        )

        for product in request.products:
            url_str = product.url
            if not url_str:
                continue
                
            # If already active, blocked, miscellaneous or in purgatory, skip
            if (url_str in active_urls or 
                url_str in blocked_urls or 
                url_str in misc_urls or 
                url_str in purgatory_urls):
                continue
                
            # Apply MOTU Relevance check
            is_relevant, reason = validate_motu_relevance(product.title)
            if not is_relevant:
                # Add to Blacklist to prevent future parsing
                bl = BlackcludedItemModel(
                    url=url_str,
                    scraped_name=product.title,
                    reason=f"Descarte automático (Importación): {reason}",
                    source_type="Peer-to-Peer"
                )
                db.add(bl)
                
                # Add history log
                history = OfferHistoryModel(
                    offer_url=url_str,
                    product_name=product.title,
                    shop_name="Wallapop",
                    price=product.price,
                    action_type="AUTO_DISCARDED_RELEVANCE",
                    details=json.dumps({"reason": reason})
                )
                db.add(history)
                blocked_urls.add(url_str)
                continue
                
            pending = PendingMatchModel(
                scraped_name=f"[Wallapop] {product.title}",
                price=product.price,
                currency="EUR",
                url=url_str,
                shop_name="Wallapop",
                source_type="Peer-to-Peer",
                image_url=product.imageUrl,
                found_at=datetime.now(timezone.utc),
            )
            db.add(pending)
            imported += 1
            
        # Clean up once more after addition, then commit
        clean_purgatory_globally(db)
        db.commit()

    logger.info(f"[Wallapop Extension] Importados {imported} productos al Purgatorio")
    return {"status": "success", "imported": imported, "total_received": len(request.products)}


@router.get("/api/radar/p2p-opportunities")
async def get_p2p_opportunities(user_id: int = 2, current_user: UserModel = Depends(get_current_user)):
    user_id = scope_user_id(current_user, user_id)
    with SessionCloud() as db:
        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            user_location = user.location

        opportunities = (
            db.query(OfferModel)
            .join(ProductModel)
            .filter(
                OfferModel.is_available == True,
                OfferModel.source_type == "Peer-to-Peer",
                ProductModel.p25_price > 0,
                OfferModel.price <= ProductModel.p25_price,
            )
            .all()
        )

        results = []
        for o in opportunities:
            saving = o.product.p25_price - o.price
            saving_pct = (saving / o.product.p25_price * 100) if o.product.p25_price > 0 else 0.0
            results.append({
                "id": o.id,
                "product_name": o.product.name,
                "ean": o.product.ean,
                "image_url": o.product.image_url,
                "price": o.price,
                "p25_price": o.product.p25_price,
                "avg_market_price": o.product.avg_market_price,
                "saving": round(saving, 2),
                "saving_pct": round(saving_pct, 1),
                "shop_name": o.shop_name,
                "url": o.url,
                "opportunity_score": o.opportunity_score,
                "landing_price": LogisticsService.get_landing_price(o.price, o.shop_name, user_location),
            })

        return sorted(results, key=lambda x: x["saving_pct"], reverse=True)
