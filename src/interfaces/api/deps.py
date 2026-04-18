from fastapi import HTTPException, Header, Request
from loguru import logger

from src.core.config import settings
from src.core.security import SecurityShield
from src.domain.models import AuthorizedDeviceModel, ScraperStatusModel
from src.infrastructure.database_cloud import SessionCloud


def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """
    Verifica la llave de la API de Eternia.
    Soporta X-API-Key para consistencia con los clientes administrativos.
    """
    if x_api_key != settings.ORACULO_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key. Access Denied.")
    return x_api_key


async def verify_device(
    request: Request,
    x_device_id: str = Header(None, alias="X-Device-ID"),
    x_device_name: str = Header("Desconocido", alias="X-Device-Name"),
    x_api_key: str = Header(None, alias="X-API-Key"),
):
    """
    Middleware protector (Ojo de Sauron).
    Valida si el dispositivo está autorizado.
    --- SOBERANÍA 3OX ---
    Si se presenta la X-API-Key correcta, el dispositivo se autoriza automáticamente.
    """
    if not x_device_id:
        raise HTTPException(
            status_code=403,
            detail="X-Device-ID header missing. Access Denied by 3OX Shield.",
        )

    with SessionCloud() as db:
        if x_api_key == settings.ORACULO_API_KEY:
            device = (
                db.query(AuthorizedDeviceModel)
                .filter(AuthorizedDeviceModel.device_id == x_device_id)
                .first()
            )
            if not device:
                device = AuthorizedDeviceModel(
                    device_id=x_device_id,
                    device_name=x_device_name,
                    is_authorized=True,
                )
                db.add(device)
            else:
                device.is_authorized = True
            db.commit()
            return x_device_id

        ip_address = request.client.host if request.client else "Unknown IP"
        is_authorized = await SecurityShield.check_access(
            x_device_id, x_device_name, ip_address, db
        )

        if not is_authorized:
            raise HTTPException(
                status_code=403,
                detail="Dispositivo no autorizado. El Gran Arquitecto ha sido notificado.",
            )
    return x_device_id


def ensure_scrapers_registered():
    """
    Fase 50: Asegura que todos los scrapers conocidos existan en ScraperStatusModel.
    Esto garantiza su visibilidad en el Purgatorio desde el primer día.
    """
    spiders_to_check = [
        "ActionToys", "Fantasia Personajes", "Frikiverso", "Electropolis",
        "Pixelatoy", "Amazon.es", "DeToyboys", "Ebay.es",
        "Vinted", "Wallapop", "ToymiEU", "Time4ActionToysDE",
        "BigBadToyStore", "Tradeinn", "DVDStoreSpain",
    ]

    with SessionCloud() as db:
        try:
            for name in spiders_to_check:
                exists = (
                    db.query(ScraperStatusModel)
                    .filter(ScraperStatusModel.spider_name.ilike(name))
                    .first()
                )
                if not exists:
                    logger.info(f"🆕 Registrando nuevo scraper en sistema: {name}")
                    db.add(ScraperStatusModel(spider_name=name, status="stopped"))
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to register scrapers: {e}")
