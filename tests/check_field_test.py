import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.infrastructure.database import SessionLocal
from src.domain.models import OfferHistoryModel, PendingMatchModel
from pathlib import Path

def check_results():
    db = SessionLocal()
    print("--- INSPECCION DE CABO DE CAMPO ---")
    
    # 1. Database History
    history = db.query(OfferHistoryModel).order_by(OfferHistoryModel.id.desc()).limit(5).all()
    print(f"\n[DB] Últimos 5 eventos de historial:")
    for h in history:
        print(f"  - {h.action_type}: {h.product_name} ({h.shop_name})")

    # 2. Purgatory Count
    pending_count = db.query(PendingMatchModel).count()
    print(f"\n[DB] Ítems en Purgatorio: {pending_count}")

    # 3. 3OX Receipts
    receipts_count = len(list(Path("vec3/var/receipts").glob("*.json")))
    print(f"\n[3OX] Recibos generados en vec3/var/receipts: {receipts_count}")

    db.close()

if __name__ == "__main__":
    check_results()
