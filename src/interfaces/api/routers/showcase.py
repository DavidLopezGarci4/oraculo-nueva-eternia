from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Any

from src.domain.models import UserModel, CollectionItemModel, ProductModel
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.schemas import PublicShowcaseOutput

router = APIRouter(tags=["showcase"])

@router.get("/api/public/showcase/{username}", response_model=PublicShowcaseOutput)
def get_public_showcase(username: str):
    """
    Retorna la colección de un usuario de forma pública si la tiene configurada como pública.
    Excluye estrictamente campos financieros (purchase_price) para proteger la privacidad.
    """
    clean_username = (username or "").strip()
    if not clean_username or "%" in clean_username or "_" in clean_username:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    with SessionCloud() as db:
        user = db.query(UserModel).filter(func.lower(UserModel.username) == clean_username.lower()).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        if not user.is_public_showcase:
            raise HTTPException(status_code=403, detail="Esta colección está configurada como privada")
            
        # Obtener los items de su colección (eager load ProductModel para evitar N+1)
        items = (
            db.query(CollectionItemModel)
            .options(joinedload(CollectionItemModel.product))
            .filter(
                CollectionItemModel.owner_id == user.id,
                CollectionItemModel.acquired == True
            )
            .all()
        )
        
        showcase_items = []
        for item in items:
            showcase_items.append({
                "id": item.id,
                "product_id": item.product_id,
                "condition": item.condition,
                "grading": item.grading,
                "notes": item.notes,
                "acquired_at": item.acquired_at,
                "product": {
                    "id": item.product.id,
                    "name": item.product.name,
                    "category": item.product.category,
                    "sub_category": item.product.sub_category,
                    "image_url": item.product.image_url,
                    "release_year": item.product.release_year,
                    "figure_id": item.product.figure_id,
                    "variant_name": item.product.variant_name,
                    "is_vintage": item.product.is_vintage,
                    "avg_market_price": item.product.avg_market_price,
                    "p25_price": item.product.p25_price
                }
            })
            
        return {
            "username": user.username,
            "location": user.location,
            "items": showcase_items,
            "total_items": len(showcase_items)
        }
