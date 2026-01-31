import asyncio
from playwright.async_api import async_playwright
import json
import os

async def test_tradeinn_robust():
    query = "masters of the universe origins"
    # url = f"https://www.tradeinn.com/es/busqueda?q={query.replace(' ', '+')}"
    base_url = "https://www.tradeinn.com/es"
    
    async with async_playwright() as p:
        # Launch with some arguments to look less like a bot
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        # Add stealth script (simple version)
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        
        print(f"Navigating to {base_url}...")
        await page.goto(base_url, wait_until="networkidle", timeout=60000)
        
        # 1. Handle Cookies
        try:
            accept_btn = page.locator('button:has-text("Aceptar todas las cookies")')
            if await accept_btn.is_visible(timeout=5000):
                print("Clicking 'Aceptar todas las cookies'...")
                await accept_btn.click()
                await asyncio.sleep(2)
        except Exception as e:
            print(f"Cookie banner not found: {e}")

        # 2. Perform Search
        try:
            print(f"Searching for '{query}'...")
            search_input = page.locator('#buscador_google')
            await search_input.click()
            await search_input.fill(query)
            await search_input.press('Enter')
            
            # Wait for navigation or results to appear
            print("Waiting for search results...")
            # We expect to be on /busqueda?q=... now or search results to load via AJAX
            await page.wait_for_selector('li.js-content-buscador_li', timeout=30000)
        except Exception as e:
            print(f"Search failed or timed out: {e}")
            await page.screenshot(path="tradeinn_robust_fail.png")
            # Trace the URL
            print(f"Current URL: {page.url}")
            await browser.close()
            return

        # 3. Extract items
        items = await page.locator('li.js-content-buscador_li').all()
        print(f"Found {len(items)} items.")
        
        for i, item in enumerate(items[:5]):
            try:
                name_el = item.locator('p#js-nombre_producto_listado')
                price_el = item.locator('p.js-precio_producto')
                link_el = item.locator('a.js-href_list_products')
                img_el = item.locator('img.js-image_list_product')
                
                name = await name_el.inner_text() if await name_el.count() > 0 else "N/A"
                price_raw = await price_el.inner_text() if await price_el.count() > 0 else "0.00"
                link = await link_el.get_attribute('href') if await link_el.count() > 0 else "N/A"
                
                # Check for shop name (sub-store)
                # Usually Tradeinn items have a "diveinn", "kidinn", etc. somewhere
                # Let's try to extract it from the link or specialized tag
                shop_name = "tradeinn"
                if link:
                    # link is usually like /kidinn/es/product-name/p/123
                    parts = link.split('/')
                    if len(parts) > 1:
                         shop_name = parts[1]
                
                print(f"[{shop_name}] {name} | {price_raw} | {link}")
            except Exception as e:
                print(f"Error parsing item {i}: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_tradeinn_robust())
