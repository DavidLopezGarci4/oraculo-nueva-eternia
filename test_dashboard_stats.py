import requests
import os

API_KEY = "eternia-shield-2026"
BASE_URL = "http://localhost:8000/api"

def test_stats(user_id):
    headers = {
        "X-API-Key": API_KEY,
        "X-Device-ID": "test-device-id"
    }
    url = f"{BASE_URL}/dashboard/stats"
    print(f"Testing GET {url} with user_id={user_id}...")
    try:
        response = requests.get(url, headers=headers, params={"user_id": user_id})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Products: {data.get('total_products')} | Owned: {data.get('owned_count')} | Wish: {data.get('wish_count')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_stats(1)
    test_stats(2)
