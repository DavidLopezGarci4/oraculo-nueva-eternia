from curl_cffi import requests
import json
import time

def scrape_wallapop_motu():
    print("Iniciando extraccion de Wallapop (MOTU Origins) via API...")
    
    # URL de la API interna identificada
    url = "https://api.wallapop.com/api/v3/general/search"
    
    params = {
        "keywords": "Masters of the Universe Origins",
        "order_by": "newest", # mas recientes
        "source": "search_box",
        "latitude": 40.4168, # Madrid por defecto
        "longitude": -3.7038
    }
    
    # Cabeceras requeridas para la API
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-ES,es;q=0.9",
        "X-DeviceOS": "0",
        "Origin": "https://es.wallapop.com",
        "Referer": "https://es.wallapop.com/"
    }

    try:
        print(f"Enviando peticion a {url}...")
        response = requests.get(url, params=params, headers=headers, impersonate="chrome110")
        
        if response.status_code != 200:
            print(f"Error: Status {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
            return

        data = response.json()
        search_objects = data.get('search_objects', [])
        
        items = []
        for obj in search_objects:
            title = obj.get('title', 'N/A')
            price = obj.get('price', 'N/A')
            currency = obj.get('currency', 'EUR')
            item_id = obj.get('id', '')
            slug = obj.get('web_slug', '')
            
            # Construir URL
            link = f"https://es.wallapop.com/item/{slug}" if slug else f"https://es.wallapop.com/item/{item_id}"
            
            items.append({
                "title": title,
                "price": f"{price} {currency}",
                "link": link
            })

        if items:
            print(f"Exito: Se han encontrado {len(items)} reliquias en la API.")
            for i, item in enumerate(items[:10], 1):
                print(f"  {i}. {item['title']} - {item['price']}")
                print(f"     URL: {item['link']}")
        else:
            print("Alerta: La API no devolvio resultados para esta busqueda.")
            if data:
                print(f"Estructura recibida: {list(data.keys())}")

    except Exception as e:
        print(f"Error critico: {e}")

if __name__ == "__main__":
    scrape_wallapop_motu()
