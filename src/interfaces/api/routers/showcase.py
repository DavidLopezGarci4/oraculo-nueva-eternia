from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from src.domain.models import UserModel, CollectionItemModel, ProductModel
from src.infrastructure.database_cloud import SessionCloud

router = APIRouter(tags=["showcase"])

@router.get("/api/public/showcase/{username}")
async def get_public_showcase(username: str):
    """
    Retorna la colección de un usuario de forma pública si la tiene configurada como pública.
    Excluye estrictamente campos financieros (purchase_price) para proteger la privacidad.
    """
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.username.ilike(username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        if not user.is_public_showcase:
            raise HTTPException(status_code=403, detail="Esta colección está configurada como privada")
            
        # Obtener los items de su colección
        items = db.query(CollectionItemModel).filter(
            CollectionItemModel.owner_id == user.id,
            CollectionItemModel.acquired == True
        ).all()
        
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
