import requests
import os

API_KEY = "eternia-shield-2026" # Default from config or .env
BASE_URL = "http://localhost:8000/api"

def test_endpoint(user_id):
    headers = {
        "X-API-Key": API_KEY,
        "X-Device-ID": "test-device-id",
        "X-Device-Name": "test-device"
    }
    url = f"{BASE_URL}/users/{user_id}"
    print(f"Testing GET {url}...")
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Body: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoint(1)
    test_endpoint(2)
