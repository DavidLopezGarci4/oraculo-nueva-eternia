import asyncio
import sys
import logging
from curl_cffi.requests import AsyncSession
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import PendingMatchModel

# Forzar salida en UTF-8 para consola en Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_url(session: AsyncSession, url: str) -> str:
    """
    Checks a URL and returns:
    - 'OK' if 200
    - 'BLOCKED' if 403 (CloudFront/WAF Block)
    - 'ROTTEN' if 404 (Deleted/Sold)
    - 'ERROR' for connection issues or other status
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://es.wallapop.com/"
    }
    
    try:
        # Petición GET rápida
        resp = await session.get(url, headers=headers, timeout=12, impersonate="chrome120")
        
        status = resp.status_code
        if status == 200:
            # Comprobar si el HTML retornado contiene CloudFront / CAPTCHA
            text = resp.text.lower()
            if "request could not be satisfied" in text or "request blocked" in text or "403 error" in text or "attention required" in text:
                return "BLOCKED"
            return "OK"
        elif status in (403, 429):
            return "BLOCKED"
        elif status == 404:
            return "ROTTEN"
        else:
            return f"STATUS_{status}"
            
    except Exception as e:
        logger.warning(f"Error checking {url}: {e}")
        return "ERROR"

async def main():
    logger.info("Iniciando auditoría y saneamiento del Purgatorio para Wallapop...")
    
    db = SessionCloud()
    try:
        # 1. Obtener ítems del Purgatorio de Wallapop
        purgatory_items = db.query(PendingMatchModel).filter(PendingMatchModel.shop_name == "Wallapop").all()
        
        logger.info(f"Se encontraron {len(purgatory_items)} ítems de Wallapop en el Purgatorio.")
        
        if not purgatory_items:
            logger.info("No hay ítems de Wallapop que auditar en el Purgatorio.")
            return
            
        # 2. Inicializar sesión de curl_cffi
        async with AsyncSession() as session:
            # Warm-up a la home
            try:
                await session.get("https://es.wallapop.com/", timeout=15, impersonate="chrome120")
                await asyncio.sleep(2)
            except Exception as e:
                logger.warning(f"Error en warm-up: {e}")
                
            items_to_delete = []
            
            for i, item in enumerate(purgatory_items, 1):
                logger.info(f"[{i}/{len(purgatory_items)}] Verificando: '{item.scraped_name}' -> {item.url}")
                
                status_res = await check_url(session, item.url)
                logger.info(f"   => Resultado: {status_res}")
                
                # Criterio de eliminación: si es bloqueado por CloudFront (WAF 403) o si el enlace está roto (404)
                if status_res in ("BLOCKED", "ROTTEN"):
                    logger.info(f"   [ALERTA] Marcado para eliminación definitiva (sin blacklist): '{item.scraped_name}'")
                    items_to_delete.append(item)
                
                # Pequeño retardo de cortesía para no saturar
                await asyncio.sleep(1.5)
                
            # 3. Proceder a la eliminación en base de datos
            if items_to_delete:
                logger.info(f"Procediendo a eliminar {len(items_to_delete)} ítems del Purgatorio...")
                for item in items_to_delete:
                    db.delete(item)
                
                db.commit()
                logger.info(f"¡Éxito! Se han eliminado {len(items_to_delete)} ítems del Purgatorio en Supabase de forma segura.")
            else:
                logger.info("No se encontraron ítems bloqueados o rotos que requeran eliminación.")
                
    except Exception as e:
        logger.error(f"Error crítico en la ejecución: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
