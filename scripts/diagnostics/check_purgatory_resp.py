import requests
import json

url = "http://127.0.0.1:8000/api/purgatory"
headers = {"X-API-Key": "eternia-shield-2026"}
params = {"limit": 25}

try:
    response = requests.get(url, headers=headers, params=params, timeout=30)
    data = response.json()
    print(f"Total items returned: {len(data)}")
    shops = {}
    for item in data:
        shop = item.get("shop_name", "Unknown")
        shops[shop] = shops.get(shop, 0) + 1
    
    print("Shop distribution in first 25 items:")
    for shop, count in shops.items():
        print(f"- {shop}: {count}")
    
    if len(data) > 0:
        print("\nLast item in page 1 info:")
        last = data[-1]
        print(f"ID: {last['id']}, Name: {last['scraped_name'][:30]}, Shop: {last['shop_name']}, Found At: {last['found_at']}")

except Exception as e:
    print(f"Error: {e}")
