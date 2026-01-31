import asyncio
from playwright.async_api import async_playwright
import json

async def test_tradeinn_playwright_refined():
    query = "masters of the universe origins"
    url = f"https://www.tradeinn.com/es/busqueda?q={query.replace(' ', '+')}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # 1. Handle Cookies
        try:
            accept_btn = page.locator('button:has-text("Aceptar todas las cookies")')
            if await accept_btn.is_visible(timeout=5000):
                print("Clicking 'Aceptar todas las cookies'...")
                await accept_btn.click()
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Cookie banner not found or error: {e}")

        # 2. Wait for items
        try:
            print("Waiting for products...")
            # Tradeinn items use .js-content-buscador_li
            await page.wait_for_selector('li.js-content-buscador_li', timeout=20000)
        except Exception as e:
            print(f"Timed out waiting for products: {e}")
            await page.screenshot(path="tradeinn_debug_refined.png")
            # Maybe there are no results? Let's check the text
            text_content = await page.content()
            if "No se han encontrado productos" in text_content:
                print("No products found for this query.")
            await browser.close()
            return

        # 3. Extract items
        items = await page.locator('li.js-content-buscador_li').all()
        print(f"Found {len(items)} items.")
        
        results = []
        for i, item in enumerate(items[:10]):
            try:
                name_el = item.locator('p#js-nombre_producto_listado')
                price_el = item.locator('p.js-precio_producto')
                link_el = item.locator('a.js-href_list_products')
                img_el = item.locator('img.js-image_list_product')
                
                name = await name_el.inner_text() if await name_el.count() > 0 else "N/A"
                price_raw = await price_el.inner_text() if await price_el.count() > 0 else "0.00"
                link = await link_el.get_attribute('href') if await link_el.count() > 0 else "N/A"
                img = await img_el.get_attribute('src') or await img_el.get_attribute('data-src') if await img_el.count() > 0 else "N/A"
                
                # The link is often absolute but let's check
                if link and not link.startswith('http'):
                    link = f"https://www.tradeinn.com{link}"
                
                print(f"- {name} | {price_raw} | {link}")
            except Exception as e:
                print(f"Error parsing item {i}: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_tradeinn_playwright_refined())
