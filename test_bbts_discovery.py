"""
BBTS (BigBadToyStore) API Discovery Script
==========================================
Este script intenta descubrir endpoints JSON internos de BBTS.
Ejecutar manualmente: python test_bbts_discovery.py
"""

import requests
from bs4 import BeautifulSoup
import json
import re

# Headers mimeticos completos
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

ENDPOINTS_TO_TEST = [
    "https://www.bigbadtoystore.com/api/Search",
    "https://www.bigbadtoystore.com/api/Products",
    "https://www.bigbadtoystore.com/graphql",
    "https://www.bigbadtoystore.com/Search?Brand=Masters%20of%20the%20Universe",
]

def test_endpoint(url):
    print(f"\n{'='*60}")
    print(f"[>] Probando: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        print(f"    Status: {response.status_code}")
        print(f"    Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            
            if 'json' in content_type:
                print("    [OK] ENDPOINT JSON ENCONTRADO!")
                try:
                    data = response.json()
                    print(f"    Keys: {list(data.keys()) if isinstance(data, dict) else type(data).__name__}")
                except:
                    print(f"    Raw: {response.text[:200]}")
                return True
            
            elif 'html' in content_type:
                soup = BeautifulSoup(response.text, 'html.parser')
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and ('__NEXT_DATA__' in script.string or 'products' in script.string.lower()):
                        print("    [!] Datos embebidos en script encontrados!")
                        return True
                
                products = soup.select('[class*="product"], [class*="item"], [data-product-id]')
                print(f"    Elementos de producto: {len(products)}")
                
        elif response.status_code == 403:
            print("    [X] Bloqueado (403)")
        elif response.status_code == 404:
            print("    [-] No encontrado (404)")
            
    except requests.exceptions.Timeout:
        print("    [T] Timeout")
    except Exception as e:
        print(f"    [E] Error: {e}")
    
    return False

def test_with_session():
    print("\n" + "="*60)
    print("[>] Probando con sesion persistente...")
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    try:
        home = session.get("https://www.bigbadtoystore.com", timeout=15)
        print(f"    Home status: {home.status_code}")
        print(f"    Cookies: {list(session.cookies.keys())}")
        
        search = session.get("https://www.bigbadtoystore.com/Search?SearchText=masters+of+the+universe+origins", timeout=20)
        print(f"    Search status: {search.status_code}")
        
        if search.status_code == 200:
            soup = BeautifulSoup(search.text, 'html.parser')
            products = soup.select('.pod-link, .search-item, [class*="SearchResult"], [class*="product"]')
            print(f"    [OK] Productos encontrados: {len(products)}")
            
            if products:
                print("\n    Primeros 3 productos:")
                for i, prod in enumerate(products[:3]):
                    name = prod.get_text(strip=True)[:60]
                    link = prod.get('href', 'N/A')
                    print(f"    {i+1}. {name}")
                    if link and link != 'N/A':
                        print(f"       -> {link[:60]}")
                    
    except Exception as e:
        print(f"    [E] Error: {e}")

def main():
    print("="*60)
    print("[*] BBTS API Discovery Tool")
    print("    Buscando puertas traseras...")
    print("="*60)
    
    found_any = False
    
    for endpoint in ENDPOINTS_TO_TEST:
        if test_endpoint(endpoint):
            found_any = True
    
    test_with_session()
    
    print("\n" + "="*60)
    if found_any:
        print("[OK] Se encontraron endpoints viables!")
    else:
        print("[X] No se encontraron APIs JSON directas.")
        print("    BBTS requiere renderizado JavaScript completo.")
        print("    Solucion: Usar Playwright con anti-deteccion.")
    print("="*60)

if __name__ == "__main__":
    main()
