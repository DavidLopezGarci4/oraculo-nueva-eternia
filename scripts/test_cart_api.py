import requests
import json

# Simulating a cart with items from multiple shops
cart_data = {
    "items": [
        {"product_name": "Skeletor BBTS", "shop_name": "BigBadToyStore", "price": 20.0, "quantity": 2},
        {"product_name": "He-Man Tradeinn", "shop_name": "Tradeinn", "price": 30.0, "quantity": 1},
        {"product_name": "Battle Cat Tradeinn", "shop_name": "Tradeinn", "price": 45.0, "quantity": 1}
    ],
    "user_id": 2
}

try:
    print("Testing Oracle Cart Calculation API...")
    url = "http://localhost:8000/api/logistics/calculate-cart"
    response = requests.post(url, json=cart_data)
    
    if response.status_code == 200:
        print("Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"Connection failed (is the API running?): {e}")
    
    # Fallback: test service directly if API is down
    print("\nAttempting direct Service test...")
    try:
        import sys
        import os
        sys.path.append(os.getcwd())
        from src.application.services.logistics_service import LogisticsService
        from src.infrastructure.database_cloud import SessionCloud
        
        result = LogisticsService.calculate_cart(cart_data["items"], "ES")
        print("Direct Service Result:")
        print(json.dumps(result, indent=2))
    except Exception as e2:
        print(f"Service test failed: {e2}")
