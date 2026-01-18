"""
Operación Rollback Selectivo: Devuelve ofertas de tiendas específicas al Purgatorio.
Mantiene la integridad atómica de la base de datos y registra la acción en el historial.
"""
import json
from datetime import datetime
from sqlalchemy import select
from loguru import logger

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import (
    OfferModel,
    PendingMatchModel,
    OfferHistoryModel,
    ProductModel
)

# Tiendas objetivo para rollback
TARGET_SHOPS = ["BigBadToyStore", "DeToyboys", "VendiloshopIT"]

def rollback_shops_to_purgatory():
    """
    Ejecuta un rollback atómico de todas las ofertas vinculadas de las tiendas objetivo.
    Las ofertas se mueven al Purgatorio (PendingMatchModel) para revisión manual.
    """
    logger.info(f"Iniciando Rollback Selectivo para: {TARGET_SHOPS}")
    
    with SessionCloud() as db:
        try:
            # 1. Obtener todas las ofertas vinculadas de las tiendas objetivo
            offers = db.query(OfferModel).filter(
                OfferModel.shop_name.in_(TARGET_SHOPS),
                OfferModel.product_id.isnot(None)
            ).all()
            
            logger.info(f"Encontradas {len(offers)} ofertas vinculadas para rollback.")
            
            reverted_count = 0
            already_in_purgatory = 0
            
            for offer in offers:
                # 2. Verificar si ya existe en el Purgatorio (evitar duplicados)
                exists = db.query(PendingMatchModel).filter(
                    PendingMatchModel.url == offer.url
                ).first()
                
                if exists:
                    already_in_purgatory += 1
                    # Solo eliminar la oferta, no duplicar en Purgatorio
                    db.delete(offer)
                    continue
                
                # 3. Obtener el nombre del producto para el Purgatorio
                product = db.query(ProductModel).filter(
                    ProductModel.id == offer.product_id
                ).first()
                product_name = product.name if product else "Unknown Product"
                
                # 4. Crear entrada en el Purgatorio
                pending = PendingMatchModel(
                    scraped_name=product_name,
                    price=offer.price,
                    currency=offer.currency,
                    url=offer.url,
                    shop_name=offer.shop_name,
                    image_url=None,
                    found_at=datetime.utcnow()
                )
                db.add(pending)
                
                # 5. Registrar en historial para auditoría
                history = OfferHistoryModel(
                    offer_url=offer.url,
                    product_name=product_name,
                    shop_name=offer.shop_name,
                    price=offer.price,
                    action_type="UNLINKED_BULK_ROLLBACK",
                    details=json.dumps({
                        "original_product_id": offer.product_id,
                        "rollback_reason": "SmartMatch inconsistency review",
                        "target_shops": TARGET_SHOPS
                    })
                )
                db.add(history)
                
                # 6. Eliminar la oferta vinculada
                db.delete(offer)
                reverted_count += 1
            
            # 7. Commit atómico
            db.commit()
            
            logger.success(f"Rollback completado: {reverted_count} ofertas enviadas al Purgatorio.")
            if already_in_purgatory > 0:
                logger.info(f"  - {already_in_purgatory} ofertas ya existían en el Purgatorio (eliminadas sin duplicar).")
            
            return {
                "status": "success",
                "reverted_count": reverted_count,
                "already_in_purgatory": already_in_purgatory,
                "target_shops": TARGET_SHOPS
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error durante rollback: {e}")
            raise

if __name__ == "__main__":
    result = rollback_shops_to_purgatory()
    print(f"\n=== RESULTADO ===")
    print(f"  Ofertas enviadas al Purgatorio: {result['reverted_count']}")
    print(f"  Ya en Purgatorio (sin duplicar): {result['already_in_purgatory']}")
    print(f"  Tiendas afectadas: {', '.join(result['target_shops'])}")
