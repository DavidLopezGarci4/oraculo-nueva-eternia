"""
Incursión Manual Asistida para WALLAPOP vía CDP (Chrome DevTools Protocol).

Réplica del flujo de Smyths Toys (`scrape_via_cdp.py`), pero adaptado a Wallapop:

  1. El usuario abre SU Chrome con el puerto de depuración 9222 activo.
  2. Navega a una (o varias) de las búsquedas de MOTU Origins, ordenadas por novedades:
       - https://es.wallapop.com/search?keywords=masters+del+universo+origins&order_by=newest
       - https://es.wallapop.com/search?keywords=masters+of+the+universe+origins&order_by=newest
       - https://es.wallapop.com/search?keywords=motu+origins&order_by=newest
  3. Ejecuta este script (o `run_wallapop_attached.ps1`).
  4. El script se conecta a esas pestañas, hace scroll para cargar los anuncios,
     extrae Nombre / Precio / URL / Imagen de cada tarjeta y los envía al PURGATORIO.

Al usar el navegador REAL del usuario (con sus cookies y su IP residencial), se evita
el bloqueo WAF de CloudFront que sufre el scraper automático de Wallapop.

Los anuncios se guardan como Peer-to-Peer, por lo que el pipeline los enruta al
Purgatorio (política "Purgatory-First") para su vinculación manual desde la web del Oráculo.
"""
import asyncio
import sys
import os
import re
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())

# Load environment
load_dotenv(override=True)

# Aseguramos salida UTF-8 en la consola de Windows (para emojis y acentos)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "https://es.wallapop.com"

# Palabras clave de ruido para descartar merchandising que no es figura Origins
JUNK_KEYWORDS = [
    "camiseta", "t-shirt", "poster", "póster", "taza", "mug", "revista", "dvd",
    "llavero", "keyring", "reproduccion", "reproducción", "repro", "sticker",
    "pegatina", "funda", "cuadro", "lampara", "lámpara",
]

# Extractor JS resiliente: lee del DOM ya renderizado de la pestaña del usuario.
# Se apoya en atributos estables (aria-label/title del enlace, [class*='price'], img)
# en lugar de nombres de clase con hash que Wallapop cambia con frecuencia.
JS_EXTRACTOR = r"""
() => {
    const items = [];
    const seen = new Set();
    document.querySelectorAll("a[href*='/item/']").forEach(a => {
        const rawHref = a.getAttribute('href') || '';
        const cleanHref = rawHref.split('?')[0];
        if (!cleanHref || seen.has(cleanHref)) return;

        // Nombre: preferimos title/aria-label (limpio) sobre el texto de la tarjeta.
        let name = (a.getAttribute('title') || a.getAttribute('aria-label') || '').trim();

        // Precio: primer elemento con clase que contenga 'price'/'Price'.
        let priceText = '';
        const priceEl = a.querySelector("[class*='price'], [class*='Price']");
        if (priceEl) {
            priceText = priceEl.textContent.trim();
        } else {
            // Fallback: buscar un patrón de precio en el texto de la tarjeta.
            const m = a.innerText.match(/(\d[\d.\s]*[.,]?\d*)\s*€/);
            if (m) priceText = m[0];
        }

        // Imagen
        const img = a.querySelector('img');
        const imageUrl = img ? (img.getAttribute('src') || img.getAttribute('data-src')) : null;

        if (!name) {
            const first = a.innerText.split('\n').map(s => s.trim()).filter(Boolean).find(s => !/€/.test(s) && !/^\d+\s*\/\s*\d+$/.test(s));
            name = first || '';
        }

        seen.add(cleanHref);
        items.push({
            name: name,
            price_text: priceText,
            href: cleanHref,
            image_url: imageUrl,
        });
    });
    return items;
}
"""


def _normalize_price(price_text: str) -> float:
    """Convierte '1.250,50 €' o '100 €' -> 1250.50 / 100.0"""
    if not price_text:
        return 0.0
    s = re.sub(r"[^\d.,]", "", price_text)
    if not s:
        return 0.0
    # Formato español: '.' miles, ',' decimales
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        # Sin coma: los puntos suelen ser separadores de miles ("1.250")
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


async def _harvest_tab(page):
    """Hace scroll en una pestaña de Wallapop y extrae sus anuncios."""
    from src.infrastructure.scrapers.base import ScrapedOffer

    print(f"🖱️  Cargando anuncios (scroll táctico) en: {page.url[:70]}...")

    # Intento no bloqueante de aceptar cookies si aparece el banner de OneTrust
    try:
        await page.evaluate(
            "() => { const b = document.querySelector('#onetrust-accept-btn-handler'); if (b) b.click(); }"
        )
    except Exception:
        pass

    # Scroll progresivo para forzar la carga perezosa de más tarjetas
    last_count = 0
    for _ in range(12):
        await page.mouse.wheel(0, 2200)
        await asyncio.sleep(1.2)
        try:
            count = await page.evaluate("() => document.querySelectorAll(\"a[href*='/item/']\").length")
        except Exception:
            count = last_count
        if count == last_count:
            # Sin nuevos elementos tras un scroll: probablemente hemos llegado al final
            if count > 0:
                break
        last_count = count

    raw_items = await page.evaluate(JS_EXTRACTOR)

    offers = []
    for it in raw_items:
        name = (it.get("name") or "").strip()
        if not name:
            continue

        # Descarte de ruido / merchandising
        if any(kw in name.lower() for kw in JUNK_KEYWORDS):
            continue

        price_val = _normalize_price(it.get("price_text", ""))
        if price_val <= 0:
            continue

        href = it.get("href", "")
        full_url = href if href.startswith("http") else f"{BASE_URL}{href}"

        offers.append(
            ScrapedOffer(
                product_name=name,
                price=price_val,
                currency="EUR",
                url=full_url,
                shop_name="Wallapop",
                image_url=it.get("image_url"),
                source_type="Peer-to-Peer",
                sale_type="Fixed_P2P",
            )
        )

    print(f"   🎁 {len(offers)} reliquias válidas extraídas de esta pestaña.")
    return offers


async def main():
    from playwright.async_api import async_playwright
    from src.infrastructure.scrapers.pipeline import ScrapingPipeline

    print("=" * 60)
    print("INCURSIÓN MANUAL ASISTIDA: WALLAPOP (CDP ATTACH)")
    print("=" * 60)
    print("🔌 Conectando al navegador Chrome en el puerto 9222...")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            print(f"❌ No se pudo conectar al puerto 9222: {e}")
            print("\nAbre Chrome con el puerto de depuración activo. Cierra Chrome del todo y ejecuta:")
            print('  chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\temp\\chrome_dev"')
            print("Luego navega a las búsquedas de Wallapop y vuelve a ejecutar este script.")
            return

        # Localizar TODAS las pestañas de búsqueda de Wallapop abiertas
        wallapop_pages = []
        for context in browser.contexts:
            for page in context.pages:
                url = (page.url or "").lower()
                if "wallapop.com" in url and ("/search" in url or "keywords=" in url):
                    wallapop_pages.append(page)

        # Fallback: cualquier pestaña de Wallapop, aunque no sea /search
        if not wallapop_pages:
            for context in browser.contexts:
                for page in context.pages:
                    if "wallapop.com" in (page.url or "").lower():
                        wallapop_pages.append(page)

        if not wallapop_pages:
            print("❌ No se encontró ninguna pestaña de Wallapop abierta.")
            print("Abre en tu Chrome (puerto 9222) una o varias de estas URLs y reintenta:")
            print("  https://es.wallapop.com/search?keywords=masters+del+universo+origins&order_by=newest")
            print("  https://es.wallapop.com/search?keywords=masters+of+the+universe+origins&order_by=newest")
            print("  https://es.wallapop.com/search?keywords=motu+origins&order_by=newest")
            await browser.close()
            return

        print(f"🎯 {len(wallapop_pages)} pestaña(s) de Wallapop detectada(s).\n")

        all_offers = []
        for page in wallapop_pages:
            try:
                offers = await _harvest_tab(page)
                all_offers.extend(offers)
            except Exception as e:
                print(f"⚠️  Error procesando pestaña {page.url[:50]}...: {e}")

        # Deduplicar por URL (varias búsquedas devuelven anuncios repetidos)
        seen = set()
        unique = []
        for o in all_offers:
            if o.url not in seen:
                seen.add(o.url)
                unique.append(o)

        print("\n" + "-" * 60)
        print(f"✅ Extracción total: {len(unique)} reliquias únicas de Wallapop.")
        print("-" * 60)
        for i, o in enumerate(unique[:15]):
            print(f"{i + 1:02d}. {o.product_name[:45]}")
            print(f"    {o.price:.2f} {o.currency} | {o.url[:60]}...")
        if len(unique) > 15:
            print(f"... y {len(unique) - 15} anuncios más.")

        if unique:
            print("\n💾 Enviando anuncios al Purgatorio (Supabase / Producción)...")
            pipeline = ScrapingPipeline([])
            new_count = pipeline.update_database(unique, shop_names=["Wallapop"])
            print(f"✅ ¡Inyección completada! {new_count} anuncios procesados hacia el Purgatorio.")
            print("   Ahora puedes vincularlos desde la sección Purgatorio de la web del Oráculo.")
        else:
            print("\n⚠️ No se extrajeron anuncios válidos. ¿La página cargó resultados?")

        # No cerramos el navegador del usuario (es su Chrome); solo soltamos la conexión CDP.


if __name__ == "__main__":
    asyncio.run(main())
