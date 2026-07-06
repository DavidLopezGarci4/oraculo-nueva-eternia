import asyncio
import os
import json
from curl_cffi.requests import AsyncSession

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

def load_dotenv():
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

async def main():
    load_dotenv()
    print("Testing Apify generic Playwright Scraper actor...")
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        print("Error: APIFY_TOKEN not found in environment.")
        return
        
    apify_url = f"https://api.apify.com/v2/acts/apify~playwright-scraper/run-sync-get-dataset-items?token={token}"
    
    # Payload for apify/playwright-scraper to fetch the category HTML
    payload = {
        "startUrls": [{"url": URL}],
        "pageFunction": "async ({ page, request, log }) => { return { html: await page.content() }; }",
        "proxyConfiguration": {"useApifyProxy": True}
    }
    
    try:
        print("Starting Apify actor run (run-sync)...")
        async with AsyncSession() as session:
            resp = await session.post(
                apify_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=180  # Give it up to 3 minutes
            )
            print(f"Status code: {resp.status_code}")
            
            if resp.status_code in [200, 201]:
                items = resp.json()
                print(f"Found {len(items)} items in dataset.")
                if items:
                    item = items[0]
                    html = item.get("html", "")
                    print(f"HTML length received: {len(html)}")
                    # Save HTML
                    with open("scratch/smyths_apify_html.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    print("Saved HTML to scratch/smyths_apify_html.html")
            else:
                print(f"Failed: {resp.text}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
