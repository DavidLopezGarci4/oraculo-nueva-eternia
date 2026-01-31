import asyncio
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
import json

async def test_tradeinn_scrape():
    query = "masters of the universe origins"
    url = f"https://www.tradeinn.com/es?q={query.replace(' ', '+')}"
    # Alternative: https://www.tradeinn.com/es/busqueda?q=...
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",
    }
    
    async with AsyncSession() as session:
        print(f"Requesting {url}...")
        resp = await session.get(url, headers=headers, impersonate="chrome120")
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            items = soup.select('li.js-content-buscador_li.product-listing-wrapper')
            print(f"Found {len(items)} items.")
            
            for item in items[:3]:
                name_tag = item.select_one('p#js-nombre_producto_listado')
                price_tag = item.select_one('p.js-precio_producto')
                link_tag = item.select_one('a.js-href_list_products')
                img_tag = item.select_one('img.js-image_list_product')
                
                name = name_tag.get_text(strip=True) if name_tag else "N/A"
                price = price_tag.get_text(strip=True) if price_tag else "N/A"
                link = link_tag.get('href') if link_tag else "N/A"
                img = img_tag.get('src') or img_tag.get('data-src') if img_tag else "N/A"
                
                print(f"- {name} | {price} | {link}")
        else:
            print("Failed to get page.")
            if "captcha" in resp.text.lower():
                print("CAPTCHA detected.")

if __name__ == "__main__":
    asyncio.run(test_tradeinn_scrape())
