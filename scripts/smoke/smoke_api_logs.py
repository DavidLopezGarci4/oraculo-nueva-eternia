import os
import requests

API_KEY = os.environ.get("ORACULO_API_KEY", "eternia-shield-2026")
BASE_URL = os.environ.get("ORACULO_BASE_URL", "http://localhost:8000")


def test_logs():
    url = f"{BASE_URL}/api/scrapers/logs"
    headers = {"X-API-Key": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        logs = response.json()
        print(f"Total Logs: {len(logs)}")
        if logs:
            print(f"Latest Log: {logs[0]['spider_name']} - {logs[0]['status']}")
    except Exception as e:
        print(f"Error calling API: {e}")


if __name__ == "__main__":
    test_logs()
