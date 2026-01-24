
from curl_cffi import requests
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

def audit_ebay_html(query="motu origins"):
    # LH_Sold=1, LH_Complete=1
    url = f"https://www.ebay.es/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
    
    print(f"Fetching eBay Sold Listings HTML: {url}")
    try:
        r = requests.get(url, headers=HEADERS, impersonate="chrome120", timeout=30)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            html = r.text
            # Look for typical patterns
            print(f"HTML Length: {len(html)}")
            
            # Save a snippet for inspection
            with open("ebay_sold_audit.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            print("HTML saved to ebay_sold_audit.html for manual inspection of patterns.")
            
            # Automatic pattern check
            if "Vendido" in html:
                print("Found 'Vendido' text in HTML!")
            if "s-item__price" in html:
                print("Found 's-item__price' class in HTML!")
        else:
            print(f"Error: {r.text[:500]}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    audit_ebay_html()
