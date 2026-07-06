import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

async def test_browser(browser_type_name):
    print(f"\n=================== Testing {browser_type_name} ===================")
    async with async_playwright() as p:
        try:
            browser_type = getattr(p, browser_type_name)
            browser = await browser_type.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0" if browser_type_name == "firefox" else "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
                viewport={'width': 1280, 'height': 720},
                locale='de-DE',
                timezone_id='Europe/Berlin',
            )
            page = await context.new_page()
            print("Navigating...")
            resp = await page.goto(URL, wait_until="load", timeout=60000)
            print(f"Status: {resp.status if resp else 'None'}")
            
            # Wait for content
            await asyncio.sleep(5)
            
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            body_text = soup.body.get_text() if soup.body else ""
            
            if "incapsula" in html.lower() or "pardon our interruption" in body_text.lower():
                print(f"❌ {browser_type_name} was BLOCKED by Imperva WAF.")
            else:
                print(f"✅ {browser_type_name} BYPASSED Imperva WAF!")
                links = soup.find_all("a", href=True)
                print(f"Found {len(links)} links")
                
            await browser.close()
        except Exception as e:
            print(f"Error with {browser_type_name}: {e}")

async def main():
    await test_browser("firefox")
    await test_browser("webkit")

if __name__ == "__main__":
    asyncio.run(main())
