import asyncio
import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())

# Load environment
load_dotenv(override=True)

SUPPORTED_SCRAPERS = [
    "SmythsToys",
    "Wallapop",
    "Vinted",
    "Ebay",
    "Amazon",
    "BBTS",
]

def get_scraper_class(name: str):
    from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper
    from src.infrastructure.scrapers.wallapop_scraper import WallapopScraper
    from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
    from src.infrastructure.scrapers.ebay_scraper import EbayScraper
    from src.infrastructure.scrapers.vinted_scraper import VintedScraper
    from src.infrastructure.scrapers.bbts_scraper import BigBadToyStoreScraper
    
    scrapers = {
        "SmythsToys": SmythsToysScraper,
        "Wallapop": WallapopScraper,
        "Amazon": AmazonScraper,
        "Ebay": EbayScraper,
        "Vinted": VintedScraper,
        "BBTS": BigBadToyStoreScraper
    }
    return scrapers.get(name)

async def execute_scraper(scraper_name: str, query: str = "auto", persist: bool = True) -> dict:
    scraper_cls = get_scraper_class(scraper_name)
    if not scraper_cls:
        return {
            "shop": scraper_name,
            "status": "No Soportado",
            "found": 0,
            "saved": 0
        }
        
    print(f"\n🚀 [Incursión] Iniciando rastreo en {scraper_name} (query='{query}')...")
    scraper = scraper_cls()
    if hasattr(scraper, "log_callback"):
        scraper.log_callback = lambda msg: print(f"[{scraper_name}] {msg}")
    
    try:
        offers = await scraper.search(query)
        print(f"✅ Incursión completada para {scraper_name}! Reliquias encontradas: {len(offers)}")
        
        for i, offer in enumerate(offers[:5]):
            print(f"   {i+1:02d}. {offer.product_name} - {offer.price} {offer.currency}")
        if len(offers) > 5:
            print(f"   ... y {len(offers) - 5} ofertas adicionales.")
            
        saved_count = 0
        if offers and persist:
            try:
                from src.infrastructure.scrapers.pipeline import ScrapingPipeline
                print(f"💾 Guardando resultados de {scraper_name} en Supabase...")
                pipeline = ScrapingPipeline([])
                saved_count = pipeline.update_database(offers, shop_names=[scraper.shop_name])
                print(f"✅ ¡Guardado completado! {saved_count} nuevas ofertas añadidas/actualizadas.")
            except Exception as dbe:
                print(f"⚠️ Error al persistir en base de datos: {dbe}")
                
        return {
            "shop": scraper_name,
            "status": "OK",
            "found": len(offers),
            "saved": saved_count
        }
    except Exception as e:
        print(f"❌ Error durante la incursión de {scraper_name}: {e}")
        return {
            "shop": scraper_name,
            "status": f"Error: {type(e).__name__}",
            "found": 0,
            "saved": 0
        }

async def run_sequential_incursion(query: str = "auto"):
    print("=" * 68)
    print(" 🏰 INICIANDO INCURSIÓN SECUENCIAL COMPLETA (TODAS LAS TIENDAS)")
    print("=" * 68)
    print(f"Modo: Secuencial por etapas | Búsqueda: '{query}'")
    print(f"Tiendas en cadena ({len(SUPPORTED_SCRAPERS)}): {', '.join(SUPPORTED_SCRAPERS)}")
    print("-" * 68)

    results = []
    for idx, shop in enumerate(SUPPORTED_SCRAPERS, 1):
        print(f"\n--- [{idx}/{len(SUPPORTED_SCRAPERS)}] ETAPA: {shop} ---")
        res = await execute_scraper(shop, query, persist=True)
        results.append(res)
        await asyncio.sleep(1.0) # Breve pausa táctica entre tiendas

    # Reporte consolidado
    print("\n" + "=" * 68)
    print(" 🏰 RESUMEN DE INCURSIÓN SECUENCIAL CONSOLIDADA")
    print("=" * 68)
    print(f"{'Tienda':<16} | {'Estado':<16} | {'Encontradas':<14} | {'Nuevas en BD':<12}")
    print("-" * 68)
    total_found = 0
    total_saved = 0
    for r in results:
        total_found += r["found"]
        total_saved += r["saved"]
        status_disp = r["status"][:16]
        print(f"{r['shop']:<16} | {status_disp:<16} | {r['found']:<14} | {r['saved']:<12}")
    print("-" * 68)
    print(f"{'TOTALES':<16} | {'-':<16} | {total_found:<14} | {total_saved:<12}")
    print("=" * 68)
    print("✨ Incursión secuencial finalizada.\n")
    return results

async def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/run_single_incursion.py <ScraperName|all> [query]")
        print(f"Tiendas soportadas: {', '.join(SUPPORTED_SCRAPERS)}, all")
        return
        
    target = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) > 2 else "auto"
    
    if target.lower() in ["all", "todas", "sequential", "completa"]:
        await run_sequential_incursion(query)
    else:
        scraper_cls = get_scraper_class(target)
        if not scraper_cls:
            print(f"Error: Scraper '{target}' no soportado.")
            print(f"Soportados: {', '.join(SUPPORTED_SCRAPERS)}, all")
            return
        await execute_scraper(target, query, persist=True)

if __name__ == "__main__":
    asyncio.run(main())
