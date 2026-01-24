
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
}

def audit_wallapop_search(query="motu origins"):
    url = "https://api.wallapop.com/api/v3/general/search"
    params = {
        "keywords": query,
        "latitude": 40.4168,
        "longitude": -3.7038,
        "country_code": "ES",
        "order_by": "newest",
        "items_count": 5
    }
    
    print(f"Auditing Wallapop Search API...")
    try:
        r = requests.get(url, params=params, headers=HEADERS, impersonate="chrome120", timeout=15)
        if r.status_code == 200:
            data = r.json()
            items = data.get("search_objects", [])
            if items:
                print("--- FULL JSON DUMP OF FIRST ITEM ---")
                print(json.dumps(items[0], indent=2))
                
                # Check for pagination/metadata
                print("\n--- METADATA ---")
                meta = {k: v for k, v in data.items() if k != 'search_objects'}
                print(json.dumps(meta, indent=2))
            else:
                print("No items found.")
        else:
            print(f"Error {r.status_code}: {r.text[:500]}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    audit_wallapop_search()
