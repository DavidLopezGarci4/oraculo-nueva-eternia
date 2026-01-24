
from curl_cffi import requests
import json
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def test_wallapop_search(query="motu origins"):
    url = "https://api.wallapop.com/api/v3/general/search"
    params = {
        "keywords": query,
        "latitude": 40.4168,
        "longitude": -3.7038,
        "country_code": "ES"
    }
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://es.wallapop.com",
        "Referer": "https://es.wallapop.com/",
    }
    
    print(f"Testing Wallapop Search with curl_cffi (impersonate='chrome110')...")
    try:
        # User tip: impersonate="chrome110" is key
        # We use curl_cffi.requests which is more similar to standard requests
        r = requests.get(url, params=params, headers=headers, impersonate="chrome110")
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            items = data.get("search_objects", [])
            print(f"Success! Found {len(items)} items.")
            if items:
                print(f"Sample item: {items[0].get('title')}")
        else:
            print(f"Error Body: {r.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_wallapop_search()
