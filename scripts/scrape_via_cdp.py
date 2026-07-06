import asyncio
import sys
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())

# Load environment
load_dotenv(override=True)

async def main():
    from playwright.async_api import async_playwright
    from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper
    from src.infrastructure.scrapers.pipeline import ScrapingPipeline
    
    print("🔌 Conectando al navegador Chrome abierto en el puerto 9222...")
    
    async with async_playwright() as p:
        try:
            # Conectar a la instancia de Chrome existente del usuario
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Buscar la pestaña activa de Smyths Toys
            target_page = None
            for context in browser.contexts:
                for page in context.pages:
                    url = page.url.lower()
                    if "smythstoys.com" in url:
                        target_page = page
                        break
                if target_page:
                    break
                    
            if not target_page:
                print("❌ Error: No se encontró ninguna pestaña abierta en Smyths Toys.")
                print("Por favor, abre Chrome en tu ordenador, navega a la categoría de MOTU de Smyths Toys, y vuelve a ejecutar este script.")
                await browser.close()
                return
                
            print(f"🎯 Pestaña encontrada! URL actual: {target_page.url}")
            print("🖱️ Simulando una pequeña lectura (scroll) para asegurar renderizado...")
            await target_page.mouse.wheel(0, 500)
            await asyncio.sleep(1.5)
            await target_page.mouse.wheel(0, -100)
            
            # Extraer el contenido HTML de la pestaña activa del usuario
            print("🔍 Extrayendo datos de la página...")
            html = await target_page.content()
            
            # Usar la lógica de parseo existente del scraper de Smyths Toys
            scraper = SmythsToysScraper()
            soup = BeautifulSoup(html, "html.parser")
            offers = scraper._parse_html(soup, set())
            
            print(f"✅ Extracción finalizada! Encontrados {len(offers)} artículos en tu pantalla.")
            print("------------------------------------------")
            for i, offer in enumerate(offers[:15]):
                print(f"{i+1:02d}. {offer.product_name}")
                print(f"    Precio: {offer.price} {offer.currency} | Disponible: {offer.is_available}")
            
            if offers:
                print("\n💾 Guardando resultados directamente en Supabase (Producción)...")
                pipeline = ScrapingPipeline([])
                new_count = pipeline.update_database(offers, shop_names=[scraper.shop_name])
                print(f"✅ ¡Guardado completado! {new_count} nuevas ofertas añadidas/actualizadas en Supabase.")
            
        except Exception as e:
            print(f"❌ Error al conectar o extraer del navegador Chrome: {e}")
            print("\nAsegúrate de haber abierto Chrome con el puerto de depuración activo:")
            print("En Windows, cierra Chrome del todo y ejecútalo desde Ejecutar (Win+R) o cmd:")
            print('chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\temp\\chrome_dev"')

if __name__ == "__main__":
    asyncio.run(main())
