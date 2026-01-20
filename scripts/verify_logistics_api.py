from fastapi.testclient import TestClient
from src.interfaces.api.main import app
import json

client = TestClient(app)

def test_logistics_integration():
    print("\n>>> Verificando integraci\u00f3n de Or\u00e1culo Log\u00edstico <<<")
    
    # 1. Verificar Dashboard
    print("\n1. Verificando Dashboard Stats...")
    response = client.get("/api/dashboard/stats?user_id=1")
    if response.status_code == 200:
        data = response.json()
        print(f"   Dashboard Stats: {json.dumps(data.get('financial'), indent=2)}")
    else:
        print(f"   Error en Dashboard: {response.status_code}")

    # 2. Verificar Colecci\u00f3n
    print("\n2. Verificando Colecci\u00f3n...")
    response = client.get("/api/collection?user_id=1")
    if response.status_code == 200:
        data = response.json()
        if data:
            item = data[0]
            print(f"   Item 0: {item.get('name')}")
            print(f"   Market Value: {item.get('market_value')}")
            print(f"   Landing Price: {item.get('landing_price')}")
        else:
            print("   Colecci\u00f3n vac\u00eda")
    else:
         print(f"   Error en Colecci\u00f3n: {response.status_code}")

    # 3. Verificar Ofertas de un producto
    print("\n3. Verificando Ofertas de Producto (ID 1)...")
    response = client.get("/api/products/1/offers")
    if response.status_code == 200:
        data = response.json()
        for o in data:
            print(f"   Tienda: {o.get('shop_name')}")
            print(f"   Precio: {o.get('price')}")
            print(f"   Landing: {o.get('landing_price')}")
            print(f"   Es mejor: {o.get('is_best')}")
            print("-" * 20)
    else:
        print(f"   Error en Ofertas: {response.status_code}")

if __name__ == "__main__":
    test_logistics_integration()
