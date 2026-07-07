import asyncio
import sys
import os
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())

# Load environment
load_dotenv(override=True)

async def main():
    from playwright.async_api import async_playwright
    from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper
    from src.infrastructure.scrapers.ebay_scraper import EbayScraper
    from src.infrastructure.scrapers.bbts_scraper import BigBadToyStoreScraper
    from src.infrastructure.scrapers.pipeline import ScrapingPipeline
    from src.infrastructure.scrapers.interface import ScrapedOffer

    print("🔌 Conectando al navegador Chrome en el puerto 9222...")
    
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
                print("❌ Error: No se encontraron pestañas abiertas en el navegador.")
                await browser.close()
                return

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

            # Si no se auto-detectó, presentar un menú interactivo en la terminal
            if not target_page:
                print("\n⚠️ No se detectó ninguna pestaña de tiendas conocidas de forma automática.")
                print("Pestañas abiertas disponibles:")
                for idx, page in enumerate(all_pages):
                    title = await page.title()
                    print(f"  [{idx}] {title[:40]} ({page.url[:50]}...)")
                print("\nSelecciona una tienda para procesar la pestaña actual:")
                print("  [1] Smyths Toys")
                print("  [2] eBay")
                print("  [3] Amazon")
                print("  [4] BigBadToyStore (BBTS)")
                print("  [x] Cancelar")
                
                choice = input("\nIntroduce opción: ").strip()
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
                
                page_choice = input(f"Introduce el número de pestaña a procesar (0-{len(all_pages)-1}): ").strip()
                try:
                    target_page = all_pages[int(page_choice)]
                except Exception:
                    print("❌ Selección de pestaña inválida.")
                    await browser.close()
                    return

            print(f"\n🎯 Pestaña seleccionada: {await target_page.title()}")
            print(f"🔗 URL: {target_page.url}")
            print(f"🚀 Iniciando extracción asistida para: {detected_shop}")
            
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
                # Extraemos la query de búsqueda de la URL o usamos "auto"
                match = re.search(r'_nkw=([^&]+)', target_page.url)
                query = match.group(1) if match else "auto"
                offers = scraper._parse_ebay_html(html, query)
                
            elif detected_shop == "BBTS":
                html = await target_page.content()
                soup = BeautifulSoup(html, "html.parser")
                scraper = BigBadToyStoreScraper()
                # BBTS tiene una lista de elementos en la página
                offers = []
                # Reutilizar parsing interno de BBTS si es viable
                product_elements = soup.find_all(class_='product-style') or soup.find_all(class_='product-card')
                for item in product_elements:
                    parsed = scraper._parse_item(item)
                    if parsed:
                        offers.append(parsed)
                        
            elif detected_shop == "Amazon":
                # Inyectar script JS para extraer directamente del DOM de Amazon
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
                
                # Normalizar precios en Python
                for item in extracted_items:
                    try:
                        # Limpiar precio: "25,99 €" -> 25.99
                        p_str = item["price_text"].replace("€", "").replace("$", "").replace("£", "").strip()
                        p_str = p_str.replace(".", "").replace(",", ".") # Formato español
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
                # Determinar nombre de la tienda para la sincronización
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
