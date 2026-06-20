import asyncio
from dotenv import load_dotenv
import os
import sys
import urllib.parse
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

# Load env variables from .env file
load_dotenv()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

async def main():
    api_key = os.environ.get("SCRAPERAPI_KEY")
    print("SCRAPERAPI_KEY:", api_key)
    
    url = "https://www.amazon.es/s?k=wwe+masters+tmnt+of+the+universe+origins"
    params = {
        "api_key": api_key,
        "url": url,
        "premium": "true",
        "country_code": "es",
        "render": "true"
    }
    
    query_string = urllib.parse.urlencode(params)
    scraperapi_url = f"http://api.scraperapi.com?{query_string}"
    
    print("Sending request to ScraperAPI with render=true...")
    async with AsyncSession() as session:
        resp = await session.get(scraperapi_url, timeout=90)
        print("Status Code:", resp.status_code)
        print("HTML length:", len(resp.text))
        
        soup = BeautifulSoup(resp.text, "html.parser")
        results = soup.select("[data-asin]")
        print(f"Found {len(results)} items with data-asin.")
        
        for idx, res in enumerate(results[:5]):
            asin = res.get("data-asin")
            title_el = res.select_one("h2 a span") or res.select_one(".a-size-medium")
            title = title_el.get_text(strip=True) if title_el else "Unknown"
            price_el = res.select_one(".a-price .a-offscreen")
            price = price_el.get_text(strip=True) if price_el else "No price"
            print(f"[{idx+1}] ASIN: {asin} - Title: {title[:55]} - Price: {price}")

if __name__ == "__main__":
    asyncio.run(main())
