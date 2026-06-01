import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

# --- Unicode Shield for Windows CMD/PowerShell ---
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Añadir el directorio raíz al path para poder importar módulos de la app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import OfferModel, PendingMatchModel, BlackcludedItemModel
from src.core.url_utils import normalize_url

def run_migration():
    print("[MIGRATE] Iniciando de-duplicacion y normalizacion en dos fases...")
    
    # =========================================================================
    # FASE 1: DE-DUPLICACION PURA (Eliminar duplicados antes de alterar URLs)
    # =========================================================================
    print("\n--- FASE 1: Identificando y eliminando duplicados en la base de datos ---")
    db1: Session = SessionCloud()
    try:
        # A. Duplicados en Purgatorio
        print("[DE-DUP] Analizando Purgatorio (pending_matches)...")
        pending_items = db1.query(PendingMatchModel).all()
        pending_by_clean = {}
        for item in pending_items:
            clean = normalize_url(item.url)
            if clean not in pending_by_clean:
                pending_by_clean[clean] = []
            pending_by_clean[clean].append(item)
            
        pending_deleted = 0
        for clean, items in pending_by_clean.items():
            if len(items) > 1:
                # Ordenar por el más reciente
                items_sorted = sorted(items, key=lambda x: x.found_at or datetime.min, reverse=True)
                # Mantener el primero, borrar el resto
                for dupe in items_sorted[1:]:
                    print(f"[MERGE-DELETE] Purgatorio: {dupe.scraped_name} ({dupe.url})")
                    db1.delete(dupe)
                    pending_deleted += 1
                    
        # B. Duplicados en Lista Negra
        print("[DE-DUP] Analizando Lista Negra (blackcluded_items)...")
        blocked_items = db1.query(BlackcludedItemModel).all()
        blocked_by_clean = {}
        for item in blocked_items:
            clean = normalize_url(item.url)
            if clean not in blocked_by_clean:
                blocked_by_clean[clean] = []
            blocked_by_clean[clean].append(item)
            
        blocked_deleted = 0
        for clean, items in blocked_by_clean.items():
            if len(items) > 1:
                # Ordenar por el más reciente
                items_sorted = sorted(items, key=lambda x: x.created_at or datetime.min, reverse=True)
                # Mantener el primero, borrar el resto
                for dupe in items_sorted[1:]:
                    print(f"[MERGE-DELETE] Lista Negra: {dupe.scraped_name} ({dupe.url})")
                    db1.delete(dupe)
                    blocked_deleted += 1
                    
        # Confirmar la fase de borrado
        if pending_deleted > 0 or blocked_deleted > 0:
            print(f"[SAVE] Confirmando eliminacion de {pending_deleted} pending_matches y {blocked_deleted} blackcluded_items...")
            db1.commit()
            print("[SUCCESS] Fase 1 completada. Base de datos libre de duplicados.")
        else:
            print("[INFO] No se encontraron duplicados conflictivos para eliminar.")
            db1.rollback()
            
    except Exception as e:
        print(f"[ERROR] Error critico en Fase 1: {e}")
        db1.rollback()
        db1.close()
        raise e
    finally:
        db1.close()

    # =========================================================================
    # FASE 2: NORMALIZACION PURA (Alterar URLs garantizando no colisiones)
    # =========================================================================
    print("\n--- FASE 2: Aplicando normalizacion de URLs limpia ---")
    db2: Session = SessionCloud()
    try:
        # A. Normalizar Ofertas
        print("[NORM] Normalizando Ofertas Activas (offers)...")
        offers = db2.query(OfferModel).all()
        offers_updated = 0
        for offer in offers:
            clean = normalize_url(offer.url)
            if offer.url != clean:
                offer.url = clean
                offers_updated += 1
                db2.add(offer)
        print(f"[SUCCESS] Ofertas normalizadas: {offers_updated}")

        # B. Normalizar Purgatorio
        print("[NORM] Normalizando Purgatorio (pending_matches)...")
        pending_items = db2.query(PendingMatchModel).all()
        pending_updated = 0
        for item in pending_items:
            clean = normalize_url(item.url)
            if item.url != clean:
                item.url = clean
                pending_updated += 1
                db2.add(item)
        print(f"[SUCCESS] Purgatorio normalizado: {pending_updated}")

        # C. Normalizar Lista Negra
        print("[NORM] Normalizando Lista Negra (blackcluded_items)...")
        blocked_items = db2.query(BlackcludedItemModel).all()
        blocked_updated = 0
        for item in blocked_items:
            clean = normalize_url(item.url)
            if item.url != clean:
                item.url = clean
                blocked_updated += 1
                db2.add(item)
        print(f"[SUCCESS] Lista Negra normalizada: {blocked_updated}")

        # Guardar todos los cambios limpios
        print("[SAVE] Confirmando cambios de normalizacion en la base de datos...")
        db2.commit()
        print("[SUCCESS] Fase 2 completada con exito total!")
        
    except Exception as e:
        print(f"[ERROR] Error critico en Fase 2: {e}")
        db2.rollback()
        raise e
    finally:
        db2.close()

if __name__ == "__main__":
    run_migration()
