import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.infrastructure.database import SessionLocal
from src.domain.models import ProductModel

def audit_products():
    db = SessionLocal()
    print("--- AUDITORIA DE PRODUCTOS (SKELETOR) ---")
    
    skeletors = db.query(ProductModel).filter(ProductModel.name.ilike("%skeletor%")).all()
    
    if not skeletors:
        print("No se encontraron productos con 'Skeletor' en el nombre.")
    else:
        for p in skeletors:
            print(f"ID: {p.id}")
            print(f"  Nombre: {p.name}")
            print(f"  Serie (sub_category): {p.sub_category}")
            print(f"  Variante: {p.variant_name}")
            print(f"  Creado el: {p.created_at}")
            print("-" * 30)

    db.close()

if __name__ == "__main__":
    audit_products()
