import asyncio
from playwright.async_api import async_playwright

async def run():
    url = "https://es.wallapop.com/search?keywords=masters%20of%20the%20universe%20origins&order_by=newest"
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            locale="es-ES"
        )
        page = await context.new_page()
        try:
            print("Navigating to Wallapop...")
            response = await page.goto(url, wait_until="networkidle", timeout=60000)
            print("Status:", response.status)
            content = await page.content()
            items = await page.locator("a[href*='/item/']").count()
            print(f"Found {items} items. 'net::ERR_ABORTED' avoided.")
        except Exception as e:
            print(f"Failed: {e}")
        finally:
            await browser.close()

asyncio.run(run())
