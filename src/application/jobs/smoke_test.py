import asyncio
import logging
import json
from datetime import datetime
from src.infrastructure.database import SessionLocal
from src.domain.models import ProductModel, OfferModel, PendingMatchModel, OfferHistoryModel, PriceHistoryModel
from src.core.notifier import NotifierService

# Configure logging to see the "Throttling" messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("smoke_test")

async def test_rate_limiting():
    logger.info("--- 🛡️ Caso 1: Validando Cortafuegos de Alertas (Rate-Limit) ---")
    notifier = NotifierService()
    
    test_msg = "🔥 ALERTA DE PRUEBA: El Oráculo está vigilando."
    
    logger.info("Enviando ráfaga de 5 mensajes idénticos...")
    results = []
    
    # We'll check the internal _should_throttle to verify behavior without actual HTTP calls
    import hashlib
    msg_hash = hashlib.md5(test_msg.encode(), usedforsecurity=False).hexdigest()
    key = f"msg_{msg_hash}"
    
    for i in range(5):
        throttled = notifier._should_throttle(key, minutes=30)
        results.append(throttled)
        status = "🚫 BLOQUEADO (Throttle)" if throttled else "✅ PROCESADO"
        logger.info(f"Mensaje {i+1}: {status}")

    if not results[0] and all(results[1:]):
        logger.info("🏆 RESULTADO: Cortafuegos operativo. Solo el primer mensaje pasó la guardia.")
        return True
    else:
        logger.error("❌ RESULTADO: Fallo en el Cortafuegos. Se permitió el spam.")
        return False

async def test_atomic_undo():
    logger.info("\n--- 💎 Caso 2: Validando la Gema del Tiempo (Undo Atómico) ---")
    db = SessionLocal()
    try:
        # Clean up any leftover from previous runs to ensure test repeatability
        db.query(PendingMatchModel).filter(PendingMatchModel.url == "https://eternal-smoke-test.com/item1").delete()
        db.query(OfferModel).filter(OfferModel.url == "https://eternal-smoke-test.com/item1").delete()
        db.query(OfferHistoryModel).filter(OfferHistoryModel.offer_url == "https://eternal-smoke-test.com/item1").delete()
        db.commit()

        # Preparation: Ensure we have a product
        product = db.query(ProductModel).first()
        if not product:
            logger.error("No hay productos en la DB para la prueba. Abortando.")
            return False

        # 1. Create a dummy Pending Item
        logger.info(f"1. Creando alma en el Purgatorio...")
        pending = PendingMatchModel(
            scraped_name="PRUEBA SMOKE TEST ITEM",
            shop_name="SmokeShop",
            price=99.99,
            url="https://eternal-smoke-test.com/item1",
            currency="EUR",
            ean="1234567890123"
        )
        db.add(pending)
        db.commit()
        pending_id = pending.id
        logger.info(f"   [OK] Item creado con ID {pending_id}")

        # 2. Simulate Link Action
        logger.info(f"2. Vinculando item al producto '{product.name}'...")
        # Create Offer
        new_offer = OfferModel(
            product_id=product.id,
            shop_name=pending.shop_name,
            price=pending.price,
            url=pending.url,
            is_available=True,
            min_price=pending.price,
            max_price=pending.price
        )
        db.add(new_offer)
        db.flush()
        
        # Create Price History
        ph = PriceHistoryModel(offer_id=new_offer.id, price=pending.price)
        db.add(ph)
        
        # Create History Log for Undo
        metadata = {"currency": pending.currency, "ean": pending.ean}
        history = OfferHistoryModel(
            offer_url=pending.url,
            product_name=pending.scraped_name,
            shop_name=pending.shop_name,
            price=pending.price,
            action_type="LINKED_MANUAL",
            details=json.dumps(metadata)
        )
        db.add(history)
        
        # Delete Pending
        db.delete(pending)
        db.commit()
        logger.info("   [OK] Vínculo realizado. Historial creado.")

        # 3. Validation: Verify state before Undo
        offer_check = db.query(OfferModel).filter(OfferModel.url == "https://eternal-smoke-test.com/item1").first()
        history_check = db.query(PriceHistoryModel).filter(PriceHistoryModel.offer_id == new_offer.id).first()
        if not offer_check or not history_check:
            logger.error("Error en la preparación: La oferta o el historial no se crearon.")
            return False

        # 4. Perform UNDO (The "Time Gem" Ritual)
        logger.info("3. Invocando la Gema del Tiempo (Undo)...")
        last_action = db.query(OfferHistoryModel).filter(
            OfferHistoryModel.offer_url == "https://eternal-smoke-test.com/item1",
            OfferHistoryModel.action_type == "LINKED_MANUAL"
        ).order_by(OfferHistoryModel.timestamp.desc()).first()

        if last_action:
            # Atomic Deletion (triggers cascades)
            offer_to_remove = db.query(OfferModel).filter(OfferModel.url == last_action.offer_url).first()
            if offer_to_remove:
                db.delete(offer_to_remove)
            
            # Re-create Pending
            meta = json.loads(last_action.details)
            undone_item = PendingMatchModel(
                scraped_name=last_action.product_name,
                shop_name=last_action.shop_name,
                price=last_action.price,
                url=last_action.offer_url,
                currency=meta.get("currency"),
                ean=meta.get("ean")
            )
            db.add(undone_item)
            
            # Update history status
            last_action.action_type = "LINKED_MANUAL_UNDONE"
            db.commit()
            logger.info("   [OK] Ritual completado.")

        # 5. Final Verification
        final_offer = db.query(OfferModel).filter(OfferModel.url == "https://eternal-smoke-test.com/item1").first()
        final_ph = db.query(PriceHistoryModel).filter(PriceHistoryModel.offer_id == new_offer.id).first()
        final_pending = db.query(PendingMatchModel).filter(PendingMatchModel.url == "https://eternal-smoke-test.com/item1").first()

        success = True
        if final_offer:
            logger.error("❌ Fallo: La oferta no fue eliminada.")
            success = False
        if final_ph:
            logger.error("❌ Fallo: El historial de precios quedó huérfano (la cascada falló).")
            success = False
        if not final_pending:
            logger.error("❌ Fallo: El ítem no volvió al Purgatorio.")
            success = False

        if success:
            logger.info("🏆 RESULTADO: Gema del Tiempo operativa. Limpieza atómica y restauración total.")
            return True
        else:
            return False

    finally:
        try:
            db.query(PendingMatchModel).filter(PendingMatchModel.url == "https://eternal-smoke-test.com/item1").delete()
            db.query(OfferHistoryModel).filter(OfferHistoryModel.offer_url == "https://eternal-smoke-test.com/item1").delete()
            db.commit()
        except Exception:
            pass
        db.close()

async def main():
    logger.info("🌌 INICIANDO RITUAL DE HUMO DEL ORÁCULO 🌌\n")
    
    r1 = await test_rate_limiting()
    r2 = await test_atomic_undo()
    
    if r1 and r2:
        logger.info("\n✅ TODAS LAS PRUEBAS COMPLETADAS CON ÉXITO. EL ORÁCULO ESTÁ LISTO PARA PRODUCCIÓN.")
    else:
        logger.error("\n❌ EL RITUAL HA FALLADO. SE REQUIERE REVISIÓN TÉCNICA.")

if __name__ == "__main__":
    asyncio.run(main())
