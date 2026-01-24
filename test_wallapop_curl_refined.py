
from curl_cffi import requests
import json
import random

# More robust headers matching a real Chrome browser
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "X-DeviceOS": "0",
    "X-Source": "web_search",
    "Origin": "https://es.wallapop.com",
    "Referer": "https://es.wallapop.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

def test_refined(query="motu origins"):
    url = "https://api.wallapop.com/api/v3/general/search"
    params = {
        "keywords": query,
        "latitude": 40.4168,
        "longitude": -3.7038,
        "country_code": "ES",
        "order_by": "newest"
    }
    
    # Testing different impersonations
    for impersonate_type in ["chrome110", "safari15_5", "chrome120"]:
        print(f"\n--- Testing with impersonate='{impersonate_type}' ---")
        try:
            r = requests.get(url, params=params, headers=HEADERS, impersonate=impersonate_type, timeout=15)
            print(f"Status Code: {r.status_code}")
            if r.status_code == 200:
                print(f"SUCCESS! Found items: {len(r.json().get('search_objects', []))}")
                break
            else:
                print(f"Response snippet: {r.text[:300]}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_refined()
