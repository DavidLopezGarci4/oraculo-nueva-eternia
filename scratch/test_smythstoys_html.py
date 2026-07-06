import asyncio
import os
from dotenv import load_dotenv
from curl_cffi.requests import AsyncSession
from playwright.async_api import async_playwright

load_dotenv()

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

async def test_curl():
    print("Testing curl-cffi...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    try:
        async with AsyncSession() as session:
            resp = await session.get(URL, headers=headers, impersonate="chrome120", timeout=15)
            print(f"Curl Status: {resp.status_code}")
            with open("scratch/smyths_curl.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print("Saved scratch/smyths_curl.html")
    except Exception as e:
        print(f"Curl Error: {e}")

async def test_scraperapi():
    print("Testing ScraperAPI...")
    api_key = os.environ.get("SCRAPERAPI_KEY")
    if not api_key:
        print("No SCRAPERAPI_KEY found in env")
        return
    import urllib.parse
    params = {"api_key": api_key, "url": URL, "country_code": "de"}
    query_string = urllib.parse.urlencode(params)
    scraperapi_url = f"http://api.scraperapi.com?{query_string}"
    try:
        async with AsyncSession() as session:
            resp = await session.get(scraperapi_url, timeout=60)
            print(f"ScraperAPI Status: {resp.status_code}")
            with open("scratch/smyths_scraperapi.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print("Saved scratch/smyths_scraperapi.html")
    except Exception as e:
        print(f"ScraperAPI Error: {e}")

async def test_playwright():
    print("Testing Playwright...")
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            resp = await page.goto(URL, timeout=60000)
            print(f"Playwright Status: {resp.status if resp else 'None'}")
            html = await page.content()
            with open("scratch/smyths_playwright.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved scratch/smyths_playwright.html")
            await browser.close()
        except Exception as e:
            print(f"Playwright Error: {e}")

async def main():
    await test_curl()
    await test_scraperapi()
    await test_playwright()

if __name__ == "__main__":
    asyncio.run(main())
