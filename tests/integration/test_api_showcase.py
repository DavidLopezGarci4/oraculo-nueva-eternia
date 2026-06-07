import pytest
from src.domain.models import UserModel, ProductModel, CollectionItemModel

def test_public_showcase_privacy_and_access(client, test_user):
    # Importar dentro del test para que los parches de conftest.py ya estén activos
    from src.interfaces.api.routers.showcase import SessionCloud
    
    username = test_user["username"]
    
    # 1. Por defecto, la colección debe ser privada y dar 403
    resp = client.get(f"/api/public/showcase/{username}")
    assert resp.status_code == 403
    assert "privada" in resp.json()["detail"]

    # 2. Configurar la colección como pública y añadir un ítem
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.username == username).first()
        assert user is not None
        user.is_public_showcase = True
        
        # Crear un producto de prueba
        product = ProductModel(
            name="He-Man Test",
            category="MOTU",
            sub_category="Origins",
            figure_id="H001",
            avg_market_price=50.0
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Grid/Item de colección
        item = CollectionItemModel(
            owner_id=user.id,
            product_id=product.id,
            acquired=True,
            condition="MOC",
            grading=9.5,
            purchase_price=20.0,
            notes="Edición especial firmada"
        )
        db.add(item)
        db.commit()

    # 3. Acceder de forma pública
    resp = client.get(f"/api/public/showcase/{username}")
    assert resp.status_code == 200
    data = resp.json()
    
    # Validar que retorna el username y el listado de items
    assert data["username"] == username
    assert data["total_items"] == 1
    
    item_data = data["items"][0]
    assert item_data["condition"] == "MOC"
    assert item_data["grading"] == 9.5
    assert item_data["notes"] == "Edición especial firmada"
    assert item_data["product"]["name"] == "He-Man Test"
    assert item_data["product"]["avg_market_price"] == 50.0
    
    # ¡CRÍTICO! Validar que no está el precio de compra del usuario en el JSON retornado
    assert "purchase_price" not in item_data
    assert "total_invested" not in item_data
    assert "invested" not in item_data

    # 4. Volver a poner como privada y comprobar
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.username == username).first()
        user.is_public_showcase = False
        db.commit()
        
    resp = client.get(f"/api/public/showcase/{username}")
    assert resp.status_code == 403
