
import requests

def test_api():
    url = "http://localhost:8000/api/admin/users"
    headers = {"X-API-Key": "eternia-shield-2026"}
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error calling API: {e}")

if __name__ == "__main__":
    test_api()
