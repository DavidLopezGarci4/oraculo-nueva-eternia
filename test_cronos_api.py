import requests

BASE_URL = "http://localhost:8000/api"

def test_price_history():
    # Get all products first to find a valid ID
    response = requests.get(f"{BASE_URL}/products")
    products = response.json()
    if not products:
        print("No products found.")
        return
    
    product_id = products[0]['id']
    print(f"Testing history for product ID: {product_id} ({products[0]['name']})")
    
    response = requests.get(f"{BASE_URL}/products/{product_id}/price-history")
    history = response.json()
    print("History Result:")
    import json
    print(json.dumps(history, indent=2))

if __name__ == "__main__":
    test_price_history()
