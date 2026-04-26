import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.infrastructure.database import SessionLocal, init_db
from src.domain.models import ProductModel, PendingMatchModel, OfferHistoryModel, PriceAlertModel, OfferModel
from src.application.services.match_service import MatchService

def verify_phase2():
    print("--- VERIFICACION FASE 2: BASTION DE DATOS ---")
    db = SessionLocal()
    
    try:
        # 1. Setup Dummy Data
        product = db.query(ProductModel).first()
        if not product:
            print("[FAIL] No hay productos en la base de datos para probar.")
            return

        print(f"[OK] Usando producto: {product.name} (ID: {product.id})")

        # 2. Add Pending Item
        pending = PendingMatchModel(
            scraped_name=f"TEST ITEM {product.name}",
            price=25.0,
            currency="EUR",
            url="https://test.com/item123",
            shop_name="TestShop"
        )
        db.add(pending)
        db.commit()
        db.refresh(pending)
        print(f"[OK] Item añadido a Purgatorio (ID: {pending.id})")

        # 3. Setup Price Alert
        alert = PriceAlertModel(
            product_id=product.id,
            user_id=1, # Assume user 1 exists
            target_price=30.0,
            is_active=True
        )
        db.add(alert)
        db.commit()
        print(f"[OK] Alerta de precio creada (Target: 30.0 EUR, Actual: 25.0 EUR)")

        # 4. Perform Match via Service
        service = MatchService(db)
        print("[ACTION] Vinculando item...")
        success, msg = service.match_item(pending.id, product.id)
        
        if success:
            print(f"[OK] {msg}")
        else:
            print(f"[FAIL] {msg}")
            return

        # 5. Verify Results
        # a. History
        history = db.query(OfferHistoryModel).filter(OfferHistoryModel.offer_url == "https://test.com/item123").first()
        if history:
            print(f"[OK] Historial registrado: {history.action_type}")
        else:
            print("[FAIL] No se encontró registro en OfferHistory")

        # b. 3OX Receipts
        receipts = list(Path("vec3/var/receipts").glob("*.json"))
        if receipts:
            print(f"[OK] Recibos 3OX generados: {len(receipts)}")
        else:
            print("[FAIL] No se generaron recibos 3OX")

        # c. Sentinel Alert Triggering
        # We need to check if the alert last_notified_at was updated
        db.refresh(alert)
        if alert.last_notified_at:
            print(f"[OK] Sentinel detectó y marcó la alerta: {alert.last_notified_at}")
        else:
            print("[FAIL] Sentinel no disparó la alerta")

        # 6. Cleanup
        db.delete(alert)
        # Offer and History persist for audit (or we can delete for clean test)
        offer = db.query(OfferModel).filter(OfferModel.url == "https://test.com/item123").first()
        if offer: db.delete(offer)
        if history: db.delete(history)
        db.commit()
        print("[OK] Limpieza completada.")

    finally:
        db.close()

if __name__ == "__main__":
    verify_phase2()
