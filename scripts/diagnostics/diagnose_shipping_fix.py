import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def diagnose_shipping_selector():
    url = "https://www.ebay.es/sch/i.html?_nkw=masters+of+the+universe+origins&LH_PrefLoc=1&_ipg=240"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".s-item__wrapper, li.s-item, li.s-card")
        
        if not items:
            print("No items found.")
            return

        for i, item in enumerate(items[:3]):
            print(f"\n--- ITEM {i+1} HTML ---")
            # Encontrar el texto "Envío" o "Gratis" para localizar el contenedor
            target_keywords = ["envío", "gratis", "shipping", "free"]
            full_text = item.get_text().lower()
            
            if any(kw in full_text for kw in target_keywords):
                print(f"Found shipping keywords in full text.")
                # Imprimir el HTML del item completo o partes interesantes
                # Intentar encontrar spans con texto de envío
                spans = item.find_all("span")
                for span in spans:
                    s_text = span.get_text().lower()
                    if any(kw in s_text for kw in target_keywords):
                        print(f"Potential Shipping Span: <span class='{span.get('class')}'> {span.get_text()} </span>")
            else:
                print("No shipping keywords found in item text.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(diagnose_shipping_selector())
