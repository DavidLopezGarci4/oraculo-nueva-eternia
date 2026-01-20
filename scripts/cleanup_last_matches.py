
import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to Python path
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import OfferModel, PendingMatchModel, OfferHistoryModel, ProductModel
from loguru import logger

def run_cleanup(dry_run=True, hours=24):
    logger.info(f"🧹 Sanación del Oráculo :: Iniciando limpieza de emparejamientos (Últimas {hours}h)...")
    if dry_run:
        logger.warning("🧪 MODO SIMULACIÓN (Dry Run) ACTIVO. No se realizarán cambios en la DB.")
    
    db = SessionCloud()
    try:
        # 1. Buscar eventos de SMART_MATCH recientes
        threshold = datetime.utcnow() - timedelta(hours=hours)
        history_events = db.query(OfferHistoryModel).filter(
            OfferHistoryModel.action_type == "SMART_MATCH",
            OfferHistoryModel.timestamp >= threshold
        ).all()
        
        logger.info(f"🔍 Encontrados {len(history_events)} eventos de matching automático.")
        
        moved_count = 0
        
        for event in history_events:
            url = event.offer_url
            logger.info(f"📦 Procesando: {event.product_name} ({url})")
            
            # Intentar recuperar detalles originales del JSON de history
            original_data = {}
            if event.details:
                try:
                    details_payload = json.loads(event.details)
                    original_data = details_payload.get("original_item", {})
                except:
                    logger.warning(f"   ⚠️ No se pudo parsear detalles para {url}")

            # 2. Buscar la oferta activa vinculada
            offer = db.query(OfferModel).filter(OfferModel.url == url).first()
            if not offer:
                logger.warning(f"   ⚠️ Oferta no encontrada en OfferModel (¿Ya fue eliminada o movida?)")
                continue
            
            # 3. Preparar datos para el Purgatorio
            # Priorizamos datos del historial, caemos en la oferta actual si faltan
            pending_data = {
                "scraped_name": original_data.get("scraped_name") or event.product_name,
                "ean": original_data.get("ean") or offer.product.ean if hasattr(offer, 'product') else None,
                "price": original_data.get("price") or offer.price,
                "currency": original_data.get("currency") or offer.currency,
                "url": url,
                "shop_name": original_data.get("shop_name") or offer.shop_name,
                "image_url": original_data.get("image_url") or (offer.product.image_url if hasattr(offer, 'product') else None),
                "source_type": original_data.get("source_type") or offer.source_type,
                "receipt_id": original_data.get("receipt_id") or offer.receipt_id,
                "opportunity_score": offer.opportunity_score,
                "found_at": event.timestamp
            }

            if not dry_run:
                # a. Crear en Purgatorio (Upsert manual por si acaso)
                exists = db.query(PendingMatchModel).filter(PendingMatchModel.url == url).first()
                if not exists:
                    pending = PendingMatchModel(**pending_data)
                    db.add(pending)
                    logger.success(f"   ✅ Movido al Purgatorio.")
                else:
                    logger.info(f"   ℹ️ Ya existía en Purgatorio, actualizando datos.")
                    for key, val in pending_data.items():
                        setattr(exists, key, val)
                
                # b. Eliminar vinculación incorrecta
                db.delete(offer)
                
                # c. Registrar reversión en historial
                reversion_history = OfferHistoryModel(
                    offer_url=url,
                    product_name=pending_data["scraped_name"],
                    shop_name=pending_data["shop_name"],
                    price=pending_data["price"],
                    action_type="UNLINKED_BY_SYSTEM",
                    details=json.dumps({"reason": "Retroactive cleanup of SmartMatch (Daily Scan fixes)"})
                )
                db.add(reversion_history)
            
            moved_count += 1

        if not dry_run:
            db.commit()
            logger.success(f"🏁 Limpieza COMPLETADA. {moved_count} items devueltos al Purgatorio.")
        else:
            logger.info(f"🏁 Simulación finalizada. Se habrían movido {moved_count} items.")
            
    except Exception as e:
        logger.error(f"❌ Error durante la limpieza: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Oracle Match Cleanup Script")
    parser.add_argument("--hours", type=int, default=24, help="Time window to check for matches")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    args = parser.parse_args()
    
    run_cleanup(dry_run=not args.apply, hours=args.hours)
