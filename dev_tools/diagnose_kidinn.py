import asyncio
from playwright.async_api import async_playwright
import sys, io

# [3OX] Unicode Resilience Shield
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def diagnose_kidinn():
    query = "masters of the universe origins"
    url = f"https://www.kidinn.com/es/busqueda?q={query.replace(' ', '+')}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        print(f"🌩️ Navegando a {url}...")
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)
            
            # Save debug
            await page.screenshot(path="kidinn_debug.png")
            print("📸 Screenshot guardado en kidinn_debug.png")
            
            html = await page.content()
            with open("kidinn_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("📄 HTML guardado en kidinn_debug.html")
            
            # Check for selectors
            items = await page.locator('li.js-content-buscador_li').all()
            print(f"📦 Elementos 'li.js-content-buscador_li' encontrados: {len(items)}")
            
            if len(items) > 0:
                name = await items[0].locator('p#js-nombre_producto_listado').inner_text()
                price = await items[0].locator('p.js-precio_producto').inner_text()
                print(f"✅ Ejemplo: {name} - {price}")
            else:
                print("❌ No se encontraron productos con el selector estándar.")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(diagnose_kidinn())
