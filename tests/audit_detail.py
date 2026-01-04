import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.infrastructure.database import SessionLocal
from src.domain.models import ProductModel
import json

def audit_target():
    db = SessionLocal()
    print("--- EXAMEN DETALLADO DE OBJETO ---")
    
    # Buscar exactamente el item que causa ruido
    item = db.query(ProductModel).filter(ProductModel.name.ilike("%Art of Engineering%")).first()
    
    if not item:
        print("[!] No se encontró 'Art of Engineering' en la base de datos.")
        return

    print(f"ID: {item.id}")
    print(f"Nombre: {item.name}")
    print(f"EAN: {item.ean}")
    print(f"Categoría: {item.category}")
    print(f"Sub-Categoría (Serie): {item.sub_category}")
    print(f"Variante: {item.variant_name}")
    print(f"ID de Figura (Sync ID): {item.figure_id}")
    print(f"Fecha de Creación: {item.created_at}")
    print(f"Última Actualización: {item.updated_at}")
    
    if item.offers:
        print(f"Ofertas vinculadas: {len(item.offers)}")
        for o in item.offers:
            print(f"  - Tienda: {o.shop_name} | URL: {o.url}")
    else:
        print("Ofertas vinculadas: Ninguna")

    db.close()

if __name__ == "__main__":
    audit_target()
