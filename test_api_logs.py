
import requests

def test_logs():
    url = "http://localhost:8000/api/scrapers/logs"
    headers = {"X-API-Key": "eternia-shield-2026"}
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
