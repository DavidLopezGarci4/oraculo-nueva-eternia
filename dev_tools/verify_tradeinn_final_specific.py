
import asyncio
from playwright.async_api import async_playwright
import sys
import io

# [3OX] Unicode Resilience Shield
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def verify_tradeinn_final_specific():
    async with async_playwright() as p:
        print("🚀 Lanzando navegador para verificación final (Specific Icon)...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        base_url = "https://www.tradeinn.com"
        query = "masters of the universe origins"
        
        print(f"🌩️ Estableciendo sesión en {base_url}...")
        await page.goto(base_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(2)
        
        # Aceptar cookies
        accept_btn = page.locator('button:has-text("Aceptar todas las cookies")')
        if await accept_btn.is_visible(timeout=5000):
            await accept_btn.click()
            print("🍪 Cookies aceptadas.")
            await asyncio.sleep(1)
            
        print(f"⌨️ Escribiendo consulta: '{query}'...")
        search_box = page.locator('#buscador_google')
        await search_box.click()
        await search_box.type(query, delay=100)
        await asyncio.sleep(1)
        
        print("🖱️ Haciendo click en la lupa específica...")
        search_icon = page.locator('#buscador_google_container img.icon-search')
        await search_icon.click()
        
        print("⏳ Verificación final...")
        try:
            await page.wait_for_selector('li.js-content-buscador_li', timeout=20000)
            items = await page.locator('li.js-content-buscador_li').all()
            print(f"✅ FINAL: Se encontraron {len(items)} productos.")
            await page.screenshot(path="tradeinn_verification_final_specific_success.png")
            
        except Exception as e:
            print(f"❌ FINAL: No se detectaron productos: {str(e)[:100]}")
            await page.screenshot(path="tradeinn_verification_final_specific_fail.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_tradeinn_final_specific())
