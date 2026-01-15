"""
Test Script para Toymi.eu y Time4ActionToys.de
==============================================
Ejecutar: python test_european_scrapers.py

Este script prueba los scrapers europeos de manera aislada
para verificar que funcionan correctamente antes de integrarlos
en GitHub Actions.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_toymi():
    print("\n" + "="*60)
    print("[TEST] Toymi.eu")
    print("="*60)
    
    from src.infrastructure.scrapers.toymi_scraper import ToymiEUScraper
    
    scraper = ToymiEUScraper()
    print(f"    Base URL: {scraper.base_url}")
    
    try:
        products = await scraper.search()
        print(f"    [OK] Productos encontrados: {len(products)}")
        
        if products:
            print("\n    Primeros 5 productos:")
            for i, p in enumerate(products[:5]):
                print(f"    {i+1}. {p.product_name[:50]}...")
                print(f"       Precio: {p.price} EUR | Disponible: {p.is_available}")
                print(f"       URL: {p.url[:60]}...")
        else:
            print("    [!] No se encontraron productos")
            
        return len(products) > 0
        
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False


async def test_time4actiontoys():
    print("\n" + "="*60)
    print("[TEST] Time4ActionToys.de")
    print("="*60)
    
    from src.infrastructure.scrapers.time4actiontoys_scraper import Time4ActionToysDEScraper
    
    scraper = Time4ActionToysDEScraper()
    print(f"    Base URL: {scraper.base_url}")
    
    try:
        products = await scraper.search()
        print(f"    [OK] Productos encontrados: {len(products)}")
        
        if products:
            print("\n    Primeros 5 productos:")
            for i, p in enumerate(products[:5]):
                print(f"    {i+1}. {p.product_name[:50]}...")
                print(f"       Precio: {p.price} EUR | Disponible: {p.is_available}")
                print(f"       URL: {p.url[:60]}...")
        else:
            print("    [!] No se encontraron productos")
            
        return len(products) > 0
        
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False


async def main():
    print("="*60)
    print("[*] Test de Scrapers Europeos - Fase 8.4b")
    print("="*60)
    
    results = {}
    
    # Test Toymi
    results['toymi'] = await test_toymi()
    
    # Pequeña pausa entre tests
    await asyncio.sleep(2)
    
    # Test Time4ActionToys
    results['time4actiontoys'] = await test_time4actiontoys()
    
    # Resumen
    print("\n" + "="*60)
    print("[RESUMEN]")
    print("="*60)
    for name, passed in results.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"    {name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n[SUCCESS] Todos los scrapers funcionan correctamente!")
    else:
        print("\n[WARNING] Algunos scrapers fallaron. Revisar logs arriba.")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
