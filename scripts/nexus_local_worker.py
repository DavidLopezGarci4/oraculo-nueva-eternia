"""
Nexus Local Bridge — Worker de Wallapop (IP Residencial).

Fase 2 del plan docs/technical/PLAN_WALLAPOP_NEXUS_LOCAL.md: resuelve trabajos de
búsqueda de Wallapop encolados desde el panel de Configuración, ejecutándolos EN
ESTA MÁQUINA (con tu IP residencial, no la del servidor/datacenter), y devuelve
los resultados al Oráculo para que caigan en el Purgatorio.

Uso:
    .venv\\Scripts\\python scripts\\nexus_local_worker.py
    (o vía run_nexus_bridge.ps1)

Variables de entorno (opcionales, .env):
    ORACULO_API_BASE_URL      URL base de la API del Oráculo (por defecto http://localhost:8000)
    ORACULO_API_KEY           Clave de administración (por defecto la de desarrollo)
    NEXUS_BRIDGE_POLL_INTERVAL Segundos entre sondeos cuando no hay trabajos (por defecto 20)
    WALLAPOP_RESIDENTIAL_PROXY Proxy opcional (normalmente innecesario aquí: esta
                               máquina YA aporta una IP residencial válida).
"""
import asyncio
import os
import socket
import sys
import time

import requests
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv(override=True)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

raw_api_url = os.environ.get("ORACULO_API_BASE_URL")
if not raw_api_url:
    # Intentar autodetectar de CORS_ORIGINS
    cors = os.environ.get("CORS_ORIGINS", "")
    for origin in cors.split(","):
        origin = origin.strip()
        if "duckdns.org" in origin or ("https://" in origin and "localhost" not in origin):
            raw_api_url = origin
            break
if not raw_api_url:
    raw_api_url = "http://localhost:8000"

ORACULO_API_BASE_URL = raw_api_url.rstrip("/")
ORACULO_API_KEY = os.environ.get("ORACULO_API_KEY", "eternia-shield-2026")
POLL_INTERVAL_SECONDS = int(os.environ.get("NEXUS_BRIDGE_POLL_INTERVAL", "20"))
WORKER_ID = socket.gethostname()

HEADERS = {"X-API-Key": ORACULO_API_KEY}


def claim_pending_job() -> dict | None:
    resp = requests.get(
        f"{ORACULO_API_BASE_URL}/api/wallapop/jobs/pending",
        params={"worker_id": WORKER_ID},
        headers=HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def submit_results(job_id: int, offers: list, blocked: bool = False, error_message: str | None = None) -> dict:
    payload = {
        "offers": offers,
        "blocked": blocked,
        "error_message": error_message,
        "worker_id": WORKER_ID,
    }
    resp = requests.post(
        f"{ORACULO_API_BASE_URL}/api/wallapop/jobs/{job_id}/results",
        json=payload,
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


async def process_job(job: dict) -> None:
    from src.infrastructure.scrapers.wallapop_manual_scraper import WallapopManualScraper
    from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper

    query = job.get("query") or "auto"
    job_id = job["id"]
    print(f"🔎 Procesando trabajo #{job_id}: '{query}'...")

    wallapop_scraper = WallapopManualScraper()
    wallapop_scraper.log_callback = lambda msg: print(f"   [Wallapop] {msg}")

    smyths_scraper = SmythsToysScraper()
    smyths_scraper.log_callback = lambda msg: print(f"   [Smyths] {msg}")

    all_offers = []
    blocked = False

    # 1. Incursión en Wallapop
    try:
        print("🚀 Iniciando extracción en Wallapop...")
        wallapop_offers = await wallapop_scraper.search(query)
        all_offers.extend(wallapop_offers)
        blocked = blocked or wallapop_scraper.blocked
    except Exception as e:
        print(f"❌ Error ejecutando la búsqueda de Wallapop para el trabajo #{job_id}: {e}")

    # 2. Incursión en Smyths Toys
    try:
        print("🚀 Iniciando extracción en Smyths Toys...")
        smyths_query = "auto" if query.lower() in ["completo", "full", "deep", "exhaustivo"] else query
        smyths_offers = await smyths_scraper.search(smyths_query)
        all_offers.extend(smyths_offers)
        blocked = blocked or smyths_scraper.blocked
    except Exception as e:
        print(f"❌ Error ejecutando la búsqueda de Smyths Toys para el trabajo #{job_id}: {e}")

    offers_payload = [
        {
            "product_name": o.product_name,
            "price": o.price,
            "currency": o.currency,
            "url": o.url,
            "shop_name": o.shop_name or ("SmythsToys" if "smythstoys" in o.url.lower() else "Wallapop"),
            "image_url": o.image_url,
            "source_type": o.source_type,
            "sale_type": o.sale_type,
        }
        for o in all_offers
    ]

    try:
        result = submit_results(job_id, offers_payload, blocked=blocked)
        print(
            f"✅ Trabajo #{job_id} -> {result['job_status']} "
            f"({len(offers_payload)} ofertas enviadas, {result.get('new_items', 0)} nuevas en el Purgatorio)"
        )
    except Exception as e:
        print(f"⚠️  No se pudieron enviar los resultados del trabajo #{job_id} al servidor: {e}")


def main_loop() -> None:
    print("=" * 60)
    print("NEXUS LOCAL BRIDGE — Worker de Wallapop (IP Residencial)")
    print("=" * 60)
    print(f"API objetivo: {ORACULO_API_BASE_URL}")
    print(f"Worker ID: {WORKER_ID}")
    print(f"Intervalo de sondeo (sin trabajos): {POLL_INTERVAL_SECONDS}s")
    print("Presiona Ctrl+C para detener.\n")

    while True:
        try:
            job = claim_pending_job()
        except Exception as e:
            print(f"⚠️  Error consultando trabajos pendientes: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        if job:
            asyncio.run(process_job(job))
        else:
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n🛑 Nexus Local Bridge detenido por el usuario.")
