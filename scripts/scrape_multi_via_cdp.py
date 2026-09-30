import asyncio
import sys
import os
import re
import socket
import subprocess
import time
from typing import Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())

# Load environment
load_dotenv(override=True)

STORE_DEFAULT_URLS = {
    "SmythsToys": "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt+desc",
    "Ebay": "https://www.ebay.es/sch/i.html?_nkw=motu+origins&_sacat=0",
    "Amazon": "https://www.amazon.es/s?k=masters+of+the+universe+origins",
    "BBTS": "https://www.bigbadtoystore.com/Search?SearchText=masters+of+the+universe+origins"
}

def find_chrome_executable() -> Optional[str]:
    common_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
    ]
    for p in common_paths:
        if p and os.path.exists(p):
            return p
    return None

def is_chrome_debug_port_open(port: int = 9222) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.8)
    try:
        res = sock.connect_ex(('127.0.0.1', port))
        return res == 0
    finally:
        sock.close()

def ensure_chrome_debug_running(port: int = 9222) -> bool:
    if is_chrome_debug_port_open(port):
        print(f"⚡ Chrome ya está abierto y escuchando en el puerto {port}.")
        return True
        
    print(f"🌐 Chrome no detectado en puerto {port}. Iniciándolo automáticamente en modo depuración...")
    chrome_path = find_chrome_executable()
    if not chrome_path:
        print("❌ Error: No se encontró chrome.exe en las rutas estándar de Windows.")
        return False
        
    user_data_dir = os.path.abspath(os.path.join(os.getcwd(), "scratch", "chrome_dev"))
    os.makedirs(user_data_dir, exist_ok=True)
    
    args = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--disable-blink-features=AutomationControlled",
        "--no-first-run",
        "--no-default-browser-check",
        "--start-maximized"
    ]
    
    try:
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(12):
            time.sleep(0.5)
            if is_chrome_debug_port_open(port):
                print(f"✅ Chrome iniciado exitosamente en puerto {port}.")
                return True
        print(f"⚠️ Chrome fue lanzado pero tardó en abrir el puerto {port}. Intentando continuar...")
        return True
    except Exception as e:
        print(f"❌ Error al iniciar Chrome automáticamente: {e}")
        return False

async def main():
    from playwright.async_api import async_playwright
    from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper
    from src.infrastructure.scrapers.ebay_scraper import EbayScraper
    from src.infrastructure.scrapers.bbts_scraper import BigBadToyStoreScraper
    from src.infrastructure.scrapers.pipeline import ScrapingPipeline
    from src.infrastructure.scrapers.base import ScrapedOffer

    print("🔌 Conectando al navegador Chrome en el puerto 9222...")
    ready = ensure_chrome_debug_running(9222)
    if not ready:
        print("❌ No se pudo iniciar ni conectar a Chrome.")
        return
    
    async with async_playwright() as p:
        try:
            # Conectar a la instancia de Chrome existente del usuario
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Escanear todas las pestañas abiertas
            all_pages = []
            for context in browser.contexts:
                for page in context.pages:
                    all_pages.append(page)
            
            if not all_pages:
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                all_pages.append(await context.new_page())

            # Intentar auto-detectar la pestaña adecuada según la URL
            target_page = None
            detected_shop = None
            
            for page in all_pages:
                url = page.url.lower()
                if "smythstoys.com" in url:
                    target_page = page
                    detected_shop = "SmythsToys"
                    break
                elif "ebay.es" in url or "ebay.com" in url:
                    target_page = page
                    detected_shop = "Ebay"
                    break
                elif "amazon.es" in url or "amazon.com" in url:
                    target_page = page
                    detected_shop = "Amazon"
                    break
                elif "bigbadtoystore.com" in url:
                    target_page = page
                    detected_shop = "BBTS"
                    break

            # Si no se auto-detectó, presentar menú interactivo
            if not target_page:
                print("\n⚠️ No se detectó ninguna pestaña de tiendas conocidas de forma automática.")
                print("Pestañas abiertas disponibles:")
                for idx, page in enumerate(all_pages):
                    title = await page.title()
                    print(f"  [{idx}] {title[:40]} ({page.url[:50]}...)")
                print("\nSelecciona una tienda para abrirla o procesarla:")
                print("  [1] Smyths Toys (Alemania)")
                print("  [2] eBay")
                print("  [3] Amazon")
                print("  [4] BigBadToyStore (BBTS)")
                print("  [x] Cancelar")
                
                choice = input("\nIntroduce opción [1-4]: ").strip()
                if choice == "1":
                    detected_shop = "SmythsToys"
                elif choice == "2":
                    detected_shop = "Ebay"
                elif choice == "3":
                    detected_shop = "Amazon"
                elif choice == "4":
                    detected_shop = "BBTS"
                else:
                    print("❌ Incursión cancelada.")
                    await browser.close()
                    return
                
                # Seleccionar la pestaña o usar la primera/crear una nueva
                target_page = all_pages[0] if all_pages else await browser.contexts[0].new_page()
                
                # Si la pestaña es en blanco o no es de la tienda, navegar automáticamente
                current_url = target_page.url.lower()
                if "about:blank" in current_url or "chrome://" in current_url or detected_shop.lower() not in current_url:
                    dest_url = STORE_DEFAULT_URLS.get(detected_shop)
                    if dest_url:
                        print(f"🌐 Navegando automáticamente a {detected_shop}: {dest_url}")
                        await target_page.goto(dest_url, wait_until="domcontentloaded")
                        await asyncio.sleep(2.0)

            print(f"\n🎯 Pestaña seleccionada: {await target_page.title()}")
            print(f"🔗 URL: {target_page.url}")
            print(f"🚀 Iniciando extracción asistida para: {detected_shop}")
            
            # Dar un momento si el usuario necesita resolver un captcha
            print("💡 Tip: Si ves un captcha o aviso de cookies en Chrome, resuélvelo ahora.")
            
            # Simular scroll para asegurar renderizado de elementos perezosos
            print("🖱️ Realizando scroll táctico...")
            await target_page.mouse.wheel(0, 800)
            await asyncio.sleep(1.0)
            await target_page.mouse.wheel(0, -300)
            await asyncio.sleep(0.5)

            offers = []
            
            # --- PARSING SEGÚN TIENDA ---
            if detected_shop == "SmythsToys":
                html = await target_page.content()
                soup = BeautifulSoup(html, "html.parser")
                scraper = SmythsToysScraper()
                offers = scraper._parse_html(soup, set())
                
            elif detected_shop == "Ebay":
                html = await target_page.content()
                scraper = EbayScraper()
                match = re.search(r'_nkw=([^&]+)', target_page.url)
                query = match.group(1) if match else "auto"
                offers = scraper._parse_ebay_html(html, query)
                
            elif detected_shop == "BBTS":
                html = await target_page.content()
                soup = BeautifulSoup(html, "html.parser")
                scraper = BigBadToyStoreScraper()
                product_elements = soup.find_all(class_='product-style') or soup.find_all(class_='product-card')
                for item in product_elements:
                    parsed = scraper._parse_item(item)
                    if parsed:
                        offers.append(parsed)
                        
            elif detected_shop == "Amazon":
                print("🔍 Extrayendo catálogo de Amazon mediante inyección JS en el DOM...")
                js_script = """
                () => {
                    let items = [];
                    document.querySelectorAll("[data-component-type='s-search-result']").forEach(el => {
                        let asin = el.getAttribute("data-asin");
                        if (!asin || asin.length !== 10) return;
                        
                        let titleEl = el.querySelector("h2 span, .s-line-clamp-2 span, h2 a span, .a-size-medium, h2");
                        let title = titleEl ? titleEl.textContent.trim() : "Unknown";
                        
                        let priceEl = el.querySelector(".a-price .a-offscreen");
                        let priceText = priceEl ? priceEl.textContent.trim() : "";
                        
                        let linkEl = el.querySelector("h2 a, a.a-link-normal");
                        let relUrl = linkEl ? linkEl.getAttribute("href") : `/dp/${asin}`;
                        let fullUrl = relUrl.startsWith("http") ? relUrl : "https://www.amazon.es" + relUrl.split("/ref=")[0];
                        
                        let imgEl = el.querySelector("img.s-image");
                        let imageUrl = imgEl ? imgEl.getAttribute("src") : null;
                        
                        if (priceText) {
                            items.push({
                                title: title,
                                price_text: priceText,
                                url: fullUrl,
                                image_url: imageUrl,
                                asin: asin
                            });
                        }
                    });
                    return items;
                }
                """
                extracted_items = await target_page.evaluate(js_script)
                
                for item in extracted_items:
                    try:
                        p_str = item["price_text"].replace("€", "").replace("$", "").replace("£", "").strip()
                        p_str = p_str.replace(".", "").replace(",", ".")
                        price = float(p_str)
                        
                        offers.append(ScrapedOffer(
                            product_name=item["title"],
                            price=price,
                            url=item["url"],
                            shop_name="Amazon.es",
                            image_url=item["image_url"],
                            source_type="Retail"
                        ))
                    except Exception:
                        continue

            print(f"\n✅ Incursión Completada! Encontradas {len(offers)} ofertas en la pestaña.")
            print("------------------------------------------")
            for i, offer in enumerate(offers[:15]):
                print(f"{i+1:02d}. {offer.product_name}")
                print(f"    Precio: {offer.price} {offer.currency} | URL: {offer.url[:60]}...")
            
            if len(offers) > 15:
                print(f"... y {len(offers) - 15} ofertas más.")

            # Guardar en base de datos
            if offers:
                print("\n💾 Inyectando ofertas directamente en Supabase (Producción)...")
                pipeline = ScrapingPipeline([])
                shop_name_mapping = {
                    "SmythsToys": "Smyths Toys",
                    "Ebay": "eBay",
                    "Amazon": "Amazon.es",
                    "BBTS": "BigBadToyStore"
                }
                shop_db_name = shop_name_mapping.get(detected_shop, "Otros")
                
                new_count = pipeline.update_database(offers, shop_names=[shop_db_name])
                print(f"✅ ¡Inyección completada! {new_count} nuevas ofertas añadidas/actualizadas en Supabase.")
            else:
                print("\n⚠️ No se encontraron ofertas válidas para procesar.")

        except Exception as e:
            print(f"❌ Error al conectar o extraer del navegador Chrome: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
