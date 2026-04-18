import os
import requests

API_KEY = os.environ.get("ORACULO_API_KEY", "eternia-shield-2026")
BASE_URL = os.environ.get("ORACULO_BASE_URL", "http://localhost:8000")


def test_api():
    url = f"{BASE_URL}/api/admin/users"
    headers = {"X-API-Key": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error calling API: {e}")


if __name__ == "__main__":
    test_api()
