import asyncio
import os
from dotenv import load_dotenv
from curl_cffi.requests import AsyncSession

load_dotenv()

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

async def test_scraperapi_premium():
    print("Testing ScraperAPI Premium...")
    api_key = os.environ.get("SCRAPERAPI_KEY")
    if not api_key:
        print("No SCRAPERAPI_KEY found in env")
        return
    import urllib.parse
    params = {
        "api_key": api_key, 
        "url": URL, 
        "country_code": "de",
        "premium": "true",
        "render": "true"
    }
    query_string = urllib.parse.urlencode(params)
    scraperapi_url = f"http://api.scraperapi.com?{query_string}"
    try:
        async with AsyncSession() as session:
            resp = await session.get(scraperapi_url, timeout=90)
            print(f"ScraperAPI Status: {resp.status_code}")
            
            # Save HTML
            with open("scratch/smyths_scraperapi_premium.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print("Saved scratch/smyths_scraperapi_premium.html")
            
            # Check content
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            body_text = soup.body.get_text() if soup.body else ""
            if "pardon our interruption" in body_text.lower() or "imperva" in body_text.lower():
                print("❌ Blocked by Imperva WAF even with ScraperAPI Premium!")
            else:
                print("✅ ScraperAPI Premium bypassed Imperva!")
                # Search for /p/ links
                p_links = soup.select("a[href*='/p/']")
                print(f"Found {len(p_links)} links containing '/p/'")
                for pl in p_links[:5]:
                    print(f"  - {pl.get_text(strip=True)}: {pl.get('href')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_scraperapi_premium())
