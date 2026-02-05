from src.application.services.logistics_service import LogisticsService
import json

def test_calc():
    items = [
        {"shop_name": "BigBadToyStore", "price": 2.99, "quantity": 1, "product_name": "Test Figure"}
    ]
    result = LogisticsService.calculate_cart(items, "ES")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_calc()
