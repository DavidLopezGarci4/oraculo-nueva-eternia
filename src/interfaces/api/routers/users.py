from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from src.application.services.logistics_service import LogisticsService
from src.domain.models import OfferModel, PendingMatchModel, ProductModel, UserModel
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_device
from src.interfaces.api.schemas import WallapopImportRequest

router = APIRouter(tags=["users"])


@router.get("/api/users/{user_id}", dependencies=[Depends(verify_device)])
async def get_user_settings(user_id: int):
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
        }


@router.post("/api/users/{user_id}/location")
async def update_user_location(user_id: int, location: str):
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        user.location = location.upper()
        db.commit()
        return {"status": "success", "location": user.location}


@router.post("/api/wallapop/import")
async def import_wallapop_products(request: WallapopImportRequest):
    imported = 0
    with SessionCloud() as db:
        for product in request.products:
            existing = db.query(PendingMatchModel).filter(PendingMatchModel.url == product.url).first()
            if existing:
                continue
            pending = PendingMatchModel(
                scraped_name=f"[Wallapop] {product.title}",
                price=product.price,
                currency="EUR",
                url=product.url,
                shop_name="Wallapop",
                source_type="Peer-to-Peer",
                image_url=product.imageUrl,
                found_at=datetime.utcnow(),
            )
            db.add(pending)
            imported += 1
        db.commit()

    logger.info(f"[Wallapop Extension] Importados {imported} productos al Purgatorio")
    return {"status": "success", "imported": imported, "total_received": len(request.products)}


@router.get("/api/radar/p2p-opportunities")
async def get_p2p_opportunities(user_id: int = 2):
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
