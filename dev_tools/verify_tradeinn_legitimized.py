
import asyncio
from playwright.async_api import async_playwright
import sys
import io

# [3OX] Unicode Resilience Shield
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def verify_tradeinn_legitimized():
    async with async_playwright() as p:
        print("🚀 Lanzando navegador para verificación legitimada...")
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
            
        url = f"{base_url}/es/busqueda?q={query.replace(' ', '+')}"
        print(f"🧭 Navegando a resultados legitimados: {url}...")
        try:
            await page.goto(url, wait_until="networkidle", timeout=45000)
        except Exception as e:
            print(f"⚠️ Aviso: Timeout en navegación: {str(e)[:50]}")
            
        print("⏳ Esperando resultados...")
        try:
            # Aumentamos el timeout para Algolia
            await page.wait_for_selector('li.js-content-buscador_li', timeout=30000)
            items = await page.locator('li.js-content-buscador_li').all()
            print(f"✅ ÉXITO: Se encontraron {len(items)} productos.")
            
            # Extraer el primero para validar
            if items:
                name = await items[0].locator('a.js-gtm-product-link').get_attribute('title')
                print(f"📦 Primer producto: {name}")
            
            await page.screenshot(path="tradeinn_verification_final_success.png")
            print("📸 Captura de pantalla guardada: tradeinn_verification_final_success.png")
            
        except Exception as e:
            print(f"❌ FALLO: No se detectaron productos: {str(e)[:100]}")
            await page.screenshot(path="tradeinn_verification_final_fail.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_tradeinn_legitimized())
