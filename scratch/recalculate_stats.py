import sys
import os
# Asegurar que el path del proyecto está en el PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.database_cloud import SessionCloud
from src.application.services.market_intelligence import MarketIntelligenceService
from src.domain.models import ProductModel
from sqlalchemy import text

def run_recalculation():
    print("[STATS ENGINE] Iniciar optimización y recálculo global de precios...")
    
    # 1. Crear índices en SQLite si no existen
    with SessionCloud() as db:
        print("Creando índices de rendimiento en la base de datos local...")
        try:
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_products_is_vintage ON products (is_vintage);"))
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_offers_is_available ON offers (is_available);"))
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_offers_source_type ON offers (source_type);"))
            db.commit()
            print("Indices creados correctamente.")
        except Exception as e:
            db.rollback()
            print(f"Error creando índices (omitir si ya existen): {e}")

    # 2. Recalcular estadísticas para todos los productos
    with SessionCloud() as db:
        products = db.query(ProductModel).all()
        total = len(products)
        print(f"Encontrados {total} productos en catálogo. Sincronizando inteligencia...")
        
        service = MarketIntelligenceService(db)
        success_count = 0
        
        for idx, product in enumerate(products, 1):
            try:
                # Ejecutar el algoritmo Convergence Nexus y actualizar p25_price
                success = service.sync_product_statistics(product.id)
                if success:
                    success_count += 1
                if idx % 50 == 0 or idx == total:
                    print(f"Progreso: {idx}/{total} productos procesados...")
            except Exception as e:
                print(f"Error al sincronizar producto {product.id} ({product.name}): {e}")
                
        db.commit()
        print(f"Sincronización finalizada. {success_count} productos actualizados con éxito.")

    # 3. Validar el resultado final
    with SessionCloud() as db:
        total_p25_gt_zero = db.query(ProductModel).filter(ProductModel.p25_price > 0).count()
        print(f"\n[VALIDACIÓN] Productos con p25_price > 0 tras recálculo: {total_p25_gt_zero} de {total}")

if __name__ == "__main__":
    run_recalculation()
