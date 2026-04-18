import json
import os
import requests

API_KEY = os.environ.get("ORACULO_API_KEY", "eternia-shield-2026")
BASE_URL = os.environ.get("ORACULO_BASE_URL", "http://127.0.0.1:8000")

url = f"{BASE_URL}/api/purgatory"
headers = {
    "X-API-Key": API_KEY,
    "Accept": "application/json",
}
params = {"limit": 1}

print(f"Testing {url} with limit=1...")
try:
    response = requests.get(url, headers=headers, params=params, timeout=30)
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error Response: {response.text}")
    else:
        print("Success! First item snippet:")
        data = response.json()
        if data:
            print(json.dumps(data[0], indent=2)[:500])
        else:
            print("Purgatory is empty.")
except Exception as e:
    print(f"Request failed: {e}")
