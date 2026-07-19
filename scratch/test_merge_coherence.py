import sys
import os
# Asegurar que el path del proyecto está en el PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel, OfferModel, CollectionItemModel, VintageProductModel
from sqlalchemy import or_

def run_test():
    print("[TEST] INICIANDO PRUEBA DE COHERENCIA DE FUSIÓN...")
    
    with SessionCloud() as db:
        # 1. Crear productos de prueba
        print("Creating test products...")
        
        # Producto Origen: Vintage Temporal
        source_product = ProductModel(
            name="Test Source Figure Vintage VINT-9999",
            ean="9999999999999",
            image_url="http://example.com/source.jpg",
            category="Masters of the Universe",
            sub_category="Vintage",
            is_vintage=True,
            figure_id="VINT-9999"
        )
        db.add(source_product)
        db.flush() # Obtener ID
        
        # Entrada auxiliar vintage
        v_entry = VintageProductModel(
            product_id=source_product.id,
            notes="Test entry"
        )
        db.add(v_entry)
        
        # Oferta origen
        source_offer = OfferModel(
            product_id=source_product.id,
            shop_name="Wallapop",
            price=25.0,
            url="http://example.com/test-offer-vintage-9999",
            is_available=True,
            is_vintage=True
        )
        db.add(source_offer)
        
        # Producto Destino: Moderno Oficial
        target_product = ProductModel(
            name="Test Target Figure Origins",
            ean="8888888888888",
            image_url="http://example.com/target.jpg",
            category="Masters of the Universe",
            sub_category="Origins",
            is_vintage=False,
            figure_id="ORIG-9999"
        )
        db.add(target_product)
        db.flush()
        
        db.commit()
        
        source_id = source_product.id
        target_id = target_product.id
        
        print(f"Test Products Created. Source ID: {source_id}, Target ID: {target_id}")
        
    # 2. Testear el nuevo endpoint de productos temporales (simulado)
    with SessionCloud() as db:
        query = db.query(ProductModel).filter(
            or_(
                ProductModel.figure_id.like("VINT-%"),
                ProductModel.figure_id.like("ORIG-%")
            )
        ).all()
        
        found_source = any(p.id == source_id for p in query)
        found_target = any(p.id == target_id for p in query)
        assert found_source, "ERROR: No se encontró el producto origen en temporales"
        assert found_target, "ERROR: No se encontró el producto destino en temporales"
        print("OK: Endpoint de Productos Temporales: OK (Productos encontrados)")

    # 3. Ejecutar la fusión (simular la lógica de api/products/merge)
    print("Executing merge simulation...")
    with SessionCloud() as db:
        source = db.query(ProductModel).filter(ProductModel.id == source_id).first()
        target = db.query(ProductModel).filter(ProductModel.id == target_id).first()
        
        # 1. Transfer offers & align is_vintage
        db.query(OfferModel).filter(OfferModel.product_id == source.id).update({
            "product_id": target.id,
            "is_vintage": target.is_vintage
        })
        
        # 2. Transfer collection items
        source_items = db.query(CollectionItemModel).filter(CollectionItemModel.product_id == source.id).all()
        for item in source_items:
            item.product_id = target.id
            
        # 3. Transfer/deduplicate vintage product entry
        source_vintage = db.query(VintageProductModel).filter(VintageProductModel.product_id == source.id).first()
        if source_vintage:
            exists = db.query(VintageProductModel).filter(VintageProductModel.product_id == target.id).first()
            if not exists:
                source_vintage.product_id = target.id
            else:
                db.delete(source_vintage)
                
        # 4. Eliminar producto origen
        db.delete(source)
        db.commit()
        print("Merge executed and committed.")

    # 4. Validar coherencia post-fusión
    with SessionCloud() as db:
        # Verificar que el origen fue eliminado
        source_exists = db.query(ProductModel).filter(ProductModel.id == source_id).first()
        assert source_exists is None, "ERROR: El producto origen no fue eliminado."
        
        # Verificar que la oferta fue transferida y su flag is_vintage es False
        offer = db.query(OfferModel).filter(OfferModel.url == "http://example.com/test-offer-vintage-9999").first()
        assert offer is not None, "ERROR: La oferta no fue transferida."
        assert offer.product_id == target_id, "ERROR: La oferta no está enlazada al target id."
        assert offer.is_vintage is False, f"ERROR: is_vintage de la oferta es {offer.is_vintage}, se esperaba False."
        
        # Limpieza de la base de datos
        print("Cleaning up test products...")
        db.delete(offer)
        
        target_db = db.query(ProductModel).filter(ProductModel.id == target_id).first()
        if target_db:
            db.delete(target_db)
            
        target_vintage = db.query(VintageProductModel).filter(VintageProductModel.product_id == target_id).first()
        if target_vintage:
            db.delete(target_vintage)
            
        db.commit()
        print("OK: FUSIÓN COHERENTE Y LIMPIEZA COMPLETADA CON ÉXITO!")

if __name__ == "__main__":
    try:
        run_test()
    except AssertionError as e:
        print(f"FAIL: ASSERTION ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: RUNTIME ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
