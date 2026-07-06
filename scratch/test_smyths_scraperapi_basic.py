import asyncio
import os
import urllib.parse
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

def load_dotenv():
    if os.path.exists(".env"):
        print("Loading environment from .env file...")
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

async def main():
    load_dotenv()
    print("Testing BASIC (non-premium, non-render) ScraperAPI request...")
    scraperapi_key = os.environ.get("SCRAPERAPI_KEY")
    if not scraperapi_key:
        print("Error: SCRAPERAPI_KEY not found in environment.")
        return
        
    params_sa = {
        "api_key": scraperapi_key,
        "url": URL
        # No premium, no render! This consumes only 1 basic credit.
    }
    query_string = urllib.parse.urlencode(params_sa)
    api_url = f"http://api.scraperapi.com?{query_string}"
    
    try:
        print("Sending request to ScraperAPI basic pool...")
        async with AsyncSession() as session:
            resp = await session.get(api_url, timeout=60)
            print(f"Response status: {resp.status_code}")
            
            html = resp.text
            soup = BeautifulSoup(html, "html.parser")
            body_text = soup.body.get_text() if soup.body else ""
            
            if "pardon our interruption" in body_text.lower() or "incapsula" in html.lower() or "incident id" in html.lower():
                print("Result: BLOCKED (Imperva blocked basic proxy)")
                with open("scratch/smyths_scraperapi_basic_blocked.html", "w", encoding="utf-8") as f:
                    f.write(html)
            else:
                print("Result: SUCCESS!")
                links = soup.find_all("a", href=True)
                p_links = [l for l in links if "/p/" in l["href"]]
                print(f"Found {len(p_links)} product links.")
                for idx, pl in enumerate(p_links[:5]):
                    print(f"  {idx}: {pl.get_text(strip=True)[:40]}")
                with open("scratch/smyths_scraperapi_basic_success.html", "w", encoding="utf-8") as f:
                    f.write(html)
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
