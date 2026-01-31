import asyncio
from playwright.async_api import async_playwright
import json

async def test_tradeinn_playwright():
    query = "masters of the universe origins"
    url = f"https://www.tradeinn.com/es?q={query.replace(' ', '+')}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        # Wait for the products to load (Algolia)
        try:
            await page.wait_for_selector('li.js-content-buscador_li.product-listing-wrapper', timeout=15000)
        except:
            print("Timed out waiting for products.")
            # Save screenshot for debugging
            await page.screenshot(path="tradeinn_debug.png")
            with open("tradeinn_debug.html", "w", encoding="utf-8") as f:
                f.write(await page.content())
            await browser.close()
            return

        items = await page.locator('li.js-content-buscador_li.product-listing-wrapper').all()
        print(f"Found {len(items)} items.")
        
        for i, item in enumerate(items[:3]):
            name = await item.locator('p#js-nombre_producto_listado').inner_text()
            price = await item.locator('p.js-precio_producto').inner_text()
            link = await item.locator('a.js-href_list_products').get_attribute('href')
            
            print(f"- {name} | {price} | {link}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_tradeinn_playwright())
