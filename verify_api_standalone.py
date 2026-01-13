import requests
import json

def test_api():
    url = "http://localhost:8000/api/dashboard/stats"
    # Header not needed for open endpoint, but harmless
    headers = {"x-api-key": "eternia-shield-2026"}
    try:
        print(f"Testing {url}...")
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        try:
            data = response.json()
            print("Response Body Identifiable Keys:")
            print(list(data.keys()))
            if "financial" in data:
                print("Financial Data:")
                print(json.dumps(data["financial"], indent=2))
        except:
            print("Response Body (Text):")
            print(response.text)
            
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    test_api()
