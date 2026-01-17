"""
Script de Rollback para Scrapers Europeos (ToymiEU y Time4ActionToys).
Mueve todos los items vinculados automáticamente al Purgatorio para revisión manual.
"""
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import OfferModel, PendingMatchModel, ProductAliasModel, OfferHistoryModel
from sqlalchemy import delete

def rollback_scrapers(shops=["ToymiEU", "Time4ActionToys"]):
    with SessionCloud() as db:
        print(f"Rollback iniciado para tiendas: {shops}")
        
        # 1. Obtener todas las ofertas vinculadas de estas tiendas
        offers = db.query(OfferModel).filter(OfferModel.shop_name.in_(shops)).all()
        print(f"Encontradas {len(offers)} ofertas vinculadas.")
        
        count = 0
        for offer in offers:
            # 2. Asegurar que existe en el Purgatorio (PendingMatchModel)
            existing_purgatory = db.query(PendingMatchModel).filter(PendingMatchModel.url == offer.url).first()
            
            p_name = offer.product.name if offer.product else "Unknown Product"
            p_image = offer.product.image_url if offer.product else None
            p_ean = offer.product.ean if offer.product else None

            if not existing_purgatory:
                new_purgatory = PendingMatchModel(
                    scraped_name=p_name,
                    ean=p_ean,
                    price=offer.price,
                    currency=offer.currency,
                    url=offer.url,
                    shop_name=offer.shop_name,
                    image_url=p_image,
                    found_at=offer.last_seen
                )
                db.add(new_purgatory)
                print(f"   Añadido al Purgatorio: {p_name[:50]}...")
            
            # 3. Eliminar Alias para evitar re-vinculación automática inmediata
            db.execute(delete(ProductAliasModel).where(ProductAliasModel.source_url == offer.url))
            
            # 4. Registrar en el historial
            history = OfferHistoryModel(
                offer_url=offer.url,
                product_name=p_name,
                shop_name=offer.shop_name,
                price=offer.price,
                action_type="PURGED",
                details="Rollback ejecutivo solicitado por el usuario (Auditoría Europea)"
            )
            db.add(history)
            
            # 5. Eliminar la oferta vinculada
            db.delete(offer)
            count += 1
            
        db.commit()
        print(f"Rollback completado. {count} items movidos al Purgatorio.")

if __name__ == "__main__":
    rollback_scrapers()
