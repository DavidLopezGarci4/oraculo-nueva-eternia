from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import OfferModel, PendingMatchModel, ProductAliasModel, OfferHistoryModel
import json

def test_unlink():
    with SessionCloud() as db:
        # 1. Buscar una oferta para testear
        offer = db.query(OfferModel).first()
        if not offer:
            print("[ERROR] No hay ofertas para testear")
            return
        
        offer_id = offer.id
        offer_url = offer.url
        product_name = offer.product.name
        print(f"[TEST] Testeando desvinculacion de: {product_name} (ID Oferta: {offer_id})")

        # 2. Ejecutar lógica de unlinking (la misma que el endpoint)
        # 1. Crear item en Purgatorio
        purgatory_item = PendingMatchModel(
            scraped_name=product_name,
            ean=None, 
            price=offer.price,
            currency=offer.currency,
            url=offer.url,
            shop_name=offer.shop_name,
            image_url=None,
            source_type=offer.source_type
        )
        db.add(purgatory_item)

        # 2. Registrar historial
        history = OfferHistoryModel(
            offer_url=offer.url,
            product_name=product_name,
            shop_name=offer.shop_name,
            price=offer.price,
            action_type="UNLINKED_MANUAL_ADMIN",
            details=json.dumps({"reason": "Test de desvinculacion manual"})
        )
        db.add(history)

        # 3. Eliminar Alias
        db.query(ProductAliasModel).filter(ProductAliasModel.source_url == offer.url).delete()

        # 4. Eliminar oferta vinculada
        db.delete(offer)

        db.commit()
        print(f"[OK] Oferta {offer_id} desvinculada.")

        # 3. Verificar resultados
        with SessionCloud() as db2:
            in_purgatory = db2.query(PendingMatchModel).filter(PendingMatchModel.url == offer_url).first()
            if in_purgatory:
                print(f"[SUCCESS] El item esta en el Purgatorio: {in_purgatory.scraped_name}")
            else:
                print("[ERROR] El item no llego al Purgatorio")
            
            offer_exists = db2.query(OfferModel).filter(OfferModel.id == offer_id).first()
            if not offer_exists:
                print("[SUCCESS] La oferta ya no existe en el catalogo")
            else:
                print("[ERROR] La oferta sigue existiendo")

if __name__ == "__main__":
    test_unlink()
