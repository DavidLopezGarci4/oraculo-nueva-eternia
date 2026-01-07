from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from loguru import logger
from src.core.config import settings
from src.infrastructure.database_cloud import SessionCloud

from datetime import datetime
app = FastAPI(title="Oráculo API Broker", version="1.0.0")

# Configurar CORS para permitir peticiones desde el frontend (Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.ORACULO_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key. Access Denied.")
    return x_api_key

class SyncAction(BaseModel):
    action_type: str
    payload: dict

class ProductOutput(BaseModel):
    id: int
    name: str
    ean: str | None
    image_url: str | None
    category: str
    sub_category: str
    figure_id: str
    variant_name: str | None

    class Config:
        from_attributes = True

from fastapi import BackgroundTasks
from src.infrastructure.scrapers.harvester import run_harvester
from src.domain.models import ProductModel, PendingMatchModel, ScraperStatusModel, BlackcludedItemModel, OfferModel, ScraperExecutionLogModel, CollectionItemModel, OfferHistoryModel
import json
from sqlalchemy import select

class CollectionToggleRequest(BaseModel):
    product_id: int
    user_id: int

class PurgatoryMatchRequest(BaseModel):
    pending_id: int
    product_id: int

class PurgatoryDiscardRequest(BaseModel):
    pending_id: int
    reason: str = "manual_discard"

class ScraperRunRequest(BaseModel):
    scraper_name: str = "harvester"  # "harvester", "all", or individual spider name
    trigger_type: str = "manual"     # "manual" or "scheduled"

@app.get("/health")
def health():
    return {"status": "ok", "message": "Eternia is online"}

@app.post("/sync/batch", dependencies=[Depends(verify_api_key)])
async def sync_batch(actions: List[SyncAction]):
    """
    Recibe un lote de acciones y las persiste en la DB Cloud (Supabase).
    """
    logger.info(f"Received sync batch with {len(actions)} actions.")
    
    synced_count = 0
    with SessionCloud() as db:
        try:
            for action in actions:
                # Ejemplo: Manejar LINK_OFFER
                if action.action_type == "LINK_OFFER":
                    pass
                synced_count += 1
            db.commit()
            return {"status": "success", "synced_count": synced_count}
        except Exception as e:
            db.rollback()
            logger.error(f"Sync error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products", response_model=List[ProductOutput])
async def get_products(sub_category: str | None = None):
    """
    Retorna el catálogo de productos desde Supabase.
    """
    with SessionCloud() as db:
        query = select(ProductModel)
        if sub_category:
            query = query.where(ProductModel.sub_category == sub_category)
        
        result = db.execute(query)
        products = result.scalars().all()
        return products

@app.get("/api/collection", response_model=List[ProductOutput])
async def get_collection(user_id: int):
    """
    Retorna la colección personal del usuario desde Supabase.
    """
    from src.domain.models import CollectionItemModel
    with SessionCloud() as db:
        query = (
            select(ProductModel)
            .join(CollectionItemModel)
            .where(CollectionItemModel.owner_id == user_id)
            .where(CollectionItemModel.acquired == True)
        )
        result = db.execute(query)
        products = result.scalars().all()
        return products

@app.post("/api/collection/toggle")
async def toggle_collection(request: CollectionToggleRequest):
    """
    Añade o elimina un producto de la colección del usuario.
    """
    from src.domain.models import CollectionItemModel
    with SessionCloud() as db:
        # Buscar si ya existe
        item = db.query(CollectionItemModel).filter(
            CollectionItemModel.product_id == request.product_id,
            CollectionItemModel.owner_id == request.user_id
        ).first()

        if item:
            # Si existe, lo eliminamos (toggle off)
            db.delete(item)
            action = "removed"
        else:
            # Si no existe, lo creamos (toggle on)
            new_item = CollectionItemModel(
                product_id=request.product_id,
                owner_id=request.user_id,
                acquired=True
            )
            db.add(new_item)
            action = "added"
        
        db.commit()
        return {"status": "success", "action": action, "product_id": request.product_id}

# --- PURGATORY ENDPOINTS ---

@app.get("/api/purgatory")
async def get_purgatory():
    """
    Retorna items en el Purgatorio con SUGERENCIAS INTELIGENTES.
    Cada item incluye una lista de posibles productos match con su score de confianza.
    """
    from src.core.brain_engine import engine
    from sqlalchemy import select
    
    with SessionCloud() as db:
        pending = db.query(PendingMatchModel).all()
        products = db.query(ProductModel).all()
        
        results = []
        for item in pending:
            # Generar sugerencias al vuelo (optimizable con caché si crece mucho)
            suggestions = []
            for p in products:
                # Usamos el engine para calcular el score
                _, score, reason = engine.calculate_match(p.name, item.scraped_name, p.ean, item.ean)
                
                # Mostrar TODAS las sugerencias con algun nivel de match (30%+), ordenadas por score
                if score > 0.30:
                    suggestions.append({
                        "product_id": p.id,
                        "name": p.name,
                        "figure_id": p.figure_id,
                        "sub_category": p.sub_category,
                        "match_score": round(score * 100, 1),
                        "reason": reason
                    })
            
            # Ordenar sugerencias por score descendente
            suggestions.sort(key=lambda x: x["match_score"], reverse=True)
            
            item_dict = {
                "id": item.id,
                "scraped_name": item.scraped_name,
                "ean": item.ean,
                "price": item.price,
                "currency": item.currency,
                "url": item.url,
                "shop_name": item.shop_name,
                "image_url": item.image_url,
                "found_at": item.found_at,
                "suggestions": suggestions[:5] # Top 5 sugerencias
            }
            results.append(item_dict)
            
        return results

# --- ADMIN / DATA PURIFICATION ENDPOINTS ---

@app.post("/api/admin/reset-smartmatches", dependencies=[Depends(verify_api_key)])
async def reset_smartmatches():
    """
    PURIFICACIÓN TOTAL: Desvincula TODAS las ofertas activas.
    Las devuelve al Purgatorio para revisión manual del Maestro con el nuevo umbral del 75%.
    """
    import json
    
    with SessionCloud() as db:
        # Obtener TODAS las ofertas vinculadas (con product_id)
        all_offers = db.query(OfferModel).filter(OfferModel.product_id.isnot(None)).all()
        
        reverted_count = 0
        for offer in all_offers:
            # Evitar duplicados en Purgatorio
            exists = db.query(PendingMatchModel).filter(PendingMatchModel.url == offer.url).first()
            if not exists:
                # Obtener nombre del producto para el Purgatorio
                product_name = offer.product.name if offer.product else "Unknown"
                
                pending = PendingMatchModel(
                    scraped_name=product_name,
                    price=offer.price,
                    currency=offer.currency,
                    url=offer.url,
                    shop_name=offer.shop_name,
                    image_url=None
                )
                db.add(pending)
            
            # Eliminar la oferta vinculada
            db.delete(offer)
            reverted_count += 1
            
        db.commit()
        return {
            "status": "success", 
            "message": f"Purificación TOTAL completada. {reverted_count} ofertas devueltas al Purgatorio."
        }

@app.post("/api/purgatory/match")
async def match_purgatory(request: PurgatoryMatchRequest):
    """Vincula un item del Purgatorio con un Producto existente y registra el evento con datos completos"""
    from src.domain.models import OfferHistoryModel
    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == request.pending_id).first()
        product = db.query(ProductModel).filter(ProductModel.id == request.product_id).first()
        
        if not item or not product:
            raise HTTPException(status_code=404, detail="Reliquia o Producto no encontrado")
        
        # Guardar copia de los datos originales para permitir reversión
        item_data = {
            "scraped_name": item.scraped_name,
            "ean": item.ean,
            "price": item.price,
            "currency": item.currency,
            "url": item.url,
            "shop_name": item.shop_name,
            "image_url": item.image_url,
            "receipt_id": item.receipt_id
        }

        new_offer = OfferModel(
            product_id=product.id,
            shop_name=item.shop_name,
            price=item.price,
            currency=item.currency,
            url=item.url,
            is_available=True
        )
        db.add(new_offer)
        
        # Historial de Vínculo (Auditoría con metadatos completos)
        history = OfferHistoryModel(
            offer_url=item.url,
            product_name=product.name,
            shop_name=item.shop_name,
            price=item.price,
            action_type="LINKED_MANUAL",
            details=json.dumps({"product_id": product.id, "original_item": item_data})
        )
        db.add(history)
        
        db.delete(item)
        db.commit()
        return {"status": "success", "message": "Vínculo sagrado establecido y registrado para la posteridad"}

@app.post("/api/purgatory/discard")
async def discard_purgatory(request: PurgatoryDiscardRequest):
    """Descarta un item del Purgatorio, lo añade a la lista negra y registra la acción"""
    from src.domain.models import OfferHistoryModel
    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == request.pending_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Reliquia no encontrada")
        
        # Guardar copia de los datos originales
        item_data = {
            "scraped_name": item.scraped_name,
            "ean": item.ean,
            "price": item.price,
            "currency": item.currency,
            "url": item.url,
            "shop_name": item.shop_name,
            "image_url": item.image_url,
            "receipt_id": item.receipt_id
        }

        bl = BlackcludedItemModel(
            url=item.url,
            scraped_name=item.scraped_name,
            reason=request.reason
        )
        db.add(bl)

        # Registrar en historial para posible reversión
        history = OfferHistoryModel(
            offer_url=item.url,
            product_name=item.scraped_name,
            shop_name=item.shop_name,
            price=item.price,
            action_type="DISCARDED",
            details=json.dumps({"reason": request.reason, "original_item": item_data})
        )
        db.add(history)

        db.delete(item)
        db.commit()
        return {"status": "success", "message": "Reliquia desterrada al abismo y registrada"}

# --- SCRAPER CONTROL ENDPOINTS ---

def run_scraper_task(scraper_name: str = "harvester", trigger_type: str = "manual"):
    """Wrapper para ejecutar recolectores y actualizar el estado en BD"""
    from datetime import datetime
    import os
    
    # 1. Marcar inicio en la base de datos
    # 1. Marcar inicio en la base de datos y crear Log
    with SessionCloud() as db:
        status = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == scraper_name).first()
        if not status:
            status = ScraperStatusModel(spider_name=scraper_name)
            db.add(status)
        status.status = "running"
        status.start_time = datetime.utcnow()
        
        # Crear entrada en la bitácora
        execution_log = ScraperExecutionLogModel(
            spider_name=scraper_name,
            status="running",
            start_time=status.start_time,
            trigger_type=trigger_type
        )
        db.add(execution_log)
        db.commit()
        log_id = execution_log.id

    items_found = 0
    error_msg = None

    try:
        if scraper_name == "harvester":
            # Ejecutar el recolector local (Playwright)
            run_harvester()
            
            # Procesar el snapshot
            from src.infrastructure.scrapers.harvester import SNAPSHOT_FILE
            from src.infrastructure.scrapers.pipeline import ScrapingPipeline
            import json
            
            if os.path.exists(SNAPSHOT_FILE):
                with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                mapped_offers = []
                for item in raw_data:
                    mapped_offers.append({
                        "product_name": item["name"],
                        "price": item["price_val"],
                        "currency": "EUR",
                        "url": item["url"],
                        "shop_name": item["store_name"],
                        "image_url": item["image_url"],
                        "is_available": True
                    })
                
                items_found = len(mapped_offers)
                pipeline = ScrapingPipeline(spiders=[])
                pipeline.update_database(mapped_offers)
                logger.info(f"Procesadas {items_found} reliquias desde el recolector local.")
        
        else:
            # Ejecutar spiders de fondo (ScrapingPipeline)
            from src.infrastructure.scrapers.pipeline import ScrapingPipeline
            from src.infrastructure.scrapers.spiders.actiontoys import ActionToysSpider
            from src.infrastructure.scrapers.spiders.fantasia import FantasiaSpider
            from src.infrastructure.scrapers.spiders.frikiverso import FrikiversoSpider
            from src.infrastructure.scrapers.spiders.electropolis import ElectropolisSpider
            from src.infrastructure.scrapers.spiders.pixelatoy import PixelatoySpider
            from src.infrastructure.scrapers.spiders.amazon import AmazonSpider
            from src.infrastructure.scrapers.spiders.dvdstorespain import DVDStoreSpainSpider
            from src.infrastructure.scrapers.spiders.kidinn import KidInnSpider
            import asyncio

            spiders_map = {
                "actiontoys": ActionToysSpider(),
                "fantasia": FantasiaSpider(),
                "frikiverso": FrikiversoSpider(),
                "electropolis": ElectropolisSpider(),
                "pixelatoy": PixelatoySpider(),
                "amazon": AmazonSpider(),
                "dvdstorespain": DVDStoreSpainSpider(),
                "kidinn": KidInnSpider()
            }

            spiders_to_run = []
            if scraper_name == "all":
                spiders_to_run = list(spiders_map.values())
            elif scraper_name in spiders_map:
                spiders_to_run = [spiders_map[scraper_name]]
            
            if spiders_to_run:
                pipeline = ScrapingPipeline(spiders_to_run)
                # Ejecutar búsqueda asíncrona (usamos "auto" o similar)
                # Nota: run_scraper_task se ejecuta en BackgroundTasks (hilo aparte)
                # pero necesitamos un loop de eventos si queremos usar await.
                # Uvicorn ya proporciona uno, pero para estar seguros:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(pipeline.run_product_search("auto"))
                loop.close()
                
                pipeline.update_database(results)
                items_found = len(results)
                logger.info(f"💾 Persistidas {items_found} ofertas tras incursión de {scraper_name}.")

        # 2. Marcar éxito en la base de datos y actualizar Log
        with SessionCloud() as db:
            status = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == scraper_name).first()
            if status:
                status.status = "completed"
                status.end_time = datetime.utcnow()
            
            # Actualizar bitácora
            log = db.query(ScraperExecutionLogModel).filter(ScraperExecutionLogModel.id == log_id).first()
            if log:
                log.status = "success"
                log.end_time = datetime.utcnow()
                log.items_found = items_found
            
            db.commit()

    except Exception as e:
        logger.error(f"Scraper Error ({scraper_name}): {e}")
        with SessionCloud() as db:
            status = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == scraper_name).first()
            if status:
                status.status = f"error: {str(e)}"
            
            # Actualizar bitácora con error
            log = db.query(ScraperExecutionLogModel).filter(ScraperExecutionLogModel.id == log_id).first()
            if log:
                log.status = "error"
                log.end_time = datetime.utcnow()
                log.error_message = str(e)
            
            db.commit()

@app.get("/api/scrapers/status", dependencies=[Depends(verify_api_key)])
async def get_scrapers_status():
    """Retorna el estado actual de los recolectores (Admin Only)"""
    with SessionCloud() as db:
        return db.query(ScraperStatusModel).all()

@app.get("/api/scrapers/logs", dependencies=[Depends(verify_api_key)])
async def get_scrapers_logs():
    """Retorna el historial de ejecuciones (Admin Only)"""
    from sqlalchemy import desc
    with SessionCloud() as db:
        return db.query(ScraperExecutionLogModel).order_by(desc(ScraperExecutionLogModel.start_time)).limit(50).all()

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Retorna métricas globales para el Tablero de Inteligencia"""
    from sqlalchemy import func
    from src.domain.models import OfferHistoryModel
    with SessionCloud() as db:
        total_products = db.query(ProductModel).count()
        owned_count = db.query(CollectionItemModel).count() # Sin filtrar por user para MVP o asumiendo user único
        
        # Valor total de la colección (suma de precios de los items en Mi Fortaleza)
        total_value = db.query(func.sum(OfferModel.price))\
            .join(ProductModel, OfferModel.product_id == ProductModel.id)\
            .join(CollectionItemModel, CollectionItemModel.product_id == ProductModel.id)\
            .scalar() or 0.0
            
        # Distribución por tienda (para el gráfico)
        shop_dist = db.query(OfferModel.shop_name, func.count(OfferModel.id))\
            .group_by(OfferModel.shop_name)\
            .all()
        
        return {
            "total_products": total_products,
            "owned_count": owned_count,
            "total_value": round(total_value, 2),
            "match_count": db.query(OfferModel).filter(OfferModel.product_id.isnot(None), OfferModel.is_available == True).count(),
            "shop_distribution": [{"shop": s, "count": c} for s, c in shop_dist]
        }

@app.get("/api/products/with-offers")
async def get_products_with_offers():
    """
    Retorna una lista de IDs de productos que tienen ofertas activas vinculadas.
    Usado para indicar visualmente qué productos tienen inteligencia de mercado.
    """
    with SessionCloud() as db:
        product_ids = db.query(OfferModel.product_id)\
            .filter(OfferModel.product_id.isnot(None), OfferModel.is_available == True)\
            .distinct()\
            .all()
        return [p[0] for p in product_ids]

@app.get("/api/products/{product_id}/offers")
async def get_product_offers(product_id: int):
    """
    Retorna la mejor oferta actual por TIENDA para un producto.
    Solo muestra la ÚLTIMA oferta válida de cada tienda, destacando la mejor global.
    """
    from sqlalchemy import desc
    with SessionCloud() as db:
        # Obtenemos TODAS las ofertas activas, ordenadas por precio asc y luego por fecha desc
        # NOTA: En una query más compleja haríamos un DISTINCT ON (shop_name) en Postgres,
        # para SQLite lo agrupamos en Python para asegurar 'La Verdad del Oráculo'.
        all_offers = db.query(OfferModel)\
            .filter(OfferModel.product_id == product_id, OfferModel.is_available == True)\
            .order_by(OfferModel.price.asc(), desc(OfferModel.last_seen))\
            .all()
            
        # Agrupación por tienda: Primera que aparece es la más barata/reciente de esa tienda
        latest_by_shop = {}
        for o in all_offers:
            if o.shop_name not in latest_by_shop:
                latest_by_shop[o.shop_name] = {
                    "id": o.id,
                    "shop_name": o.shop_name,
                    "price": o.price,
                    "url": o.url,
                    "last_seen": o.last_seen.isoformat(),
                    "min_historical": o.min_price or o.price,
                    "is_best": False # Se marcará abajo
                }
        
        results = list(latest_by_shop.values())
        if results:
            # Marcar la mejor global (la primera ya suele serlo por el order_by price.asc)
            results.sort(key=lambda x: x["price"])
            results[0]["is_best"] = True
            
        return results

@app.get("/api/dashboard/top-deals")
async def get_top_deals(user_id: int = 2):
    """
    Retorna las 20 mejores ofertas actuales de items NO CAPTURADOS.
    """
    with SessionCloud() as db:
        # Obtenemos IDs de productos ya capturados
        owned_ids = [p[0] for p in db.query(CollectionItemModel.product_id).filter(CollectionItemModel.owner_id == user_id).all()]

        offers = db.query(OfferModel)\
            .join(ProductModel)\
            .filter(
                OfferModel.is_available == True,
                OfferModel.product_id.notin_(owned_ids) if owned_ids else True
            )\
            .order_by(OfferModel.price.asc())\
            .limit(20)\
            .all()
        
        return [
            {
                "id": o.id,
                "product_name": o.product.name,
                "price": o.price,
                "shop_name": o.shop_name,
                "url": o.url,
                "image_url": o.product.image_url
            } for o in offers
        ]

@app.get("/api/dashboard/match-stats")
async def get_dashboard_match_stats():
    """Retorna estadísticas de conquistas ACTUALES por tienda (enlaces activos)"""
    from sqlalchemy import func
    with SessionCloud() as db:
        stats = db.query(
            OfferModel.shop_name.label("shop"), 
            func.count(OfferModel.id).label("count")
        ).filter(
            OfferModel.product_id.isnot(None),
            OfferModel.is_available == True
        ).group_by(
            OfferModel.shop_name
        ).all()
        
        return [{"shop": s.shop, "count": s.count} for s in stats]

@app.get("/api/dashboard/history")
async def get_dashboard_history():
    """Retorna los movimientos recientes de almas (vínculos/descartes)"""
    from sqlalchemy import desc
    from src.domain.models import OfferHistoryModel
    with SessionCloud() as db:
        history = db.query(OfferHistoryModel)\
            .order_by(desc(OfferHistoryModel.timestamp))\
            .limit(10)\
            .all()
            
        return [{
            "id": h.id,
            "product_name": h.product_name,
            "shop_name": h.shop_name,
            "price": h.price,
            "action_type": h.action_type,
            "timestamp": h.timestamp.isoformat()
        } for h in history]

@app.post("/api/dashboard/revert")
async def revert_action(request: dict):
    """Revierte una acción de vínculo o descarte, con soporte para reconstrucción retroactiva"""
    history_id = request.get("history_id")
    if not history_id:
        raise HTTPException(status_code=400, detail="ID de historial requerido")
        
    with SessionCloud() as db:
        history = db.query(OfferHistoryModel).filter(OfferHistoryModel.id == history_id).first()
        if not history:
            raise HTTPException(status_code=404, detail="Entrada de historial no encontrada")
            
        # Intentar obtener metadatos completos
        original_item = None
        try:
            details_json = json.loads(history.details)
            # El JSON puede ser {"original_item": {...}} o un formato anterior
            if isinstance(details_json, dict):
                 original_item = details_json.get("original_item")
        except:
            # Fallback retroactivo: No hay JSON, usamos campos base de la tabla history
            logger.warning(f"Reconstruction Fallback for History ID {history_id}: No JSON metadata found.")

        # Si no hay metadatos guardados, usamos lo mínimo disponible en las columnas
        if not original_item:
            original_item = {
                "scraped_name": history.product_name,
                "ean": None,
                "price": history.price,
                "currency": "EUR",
                "url": history.offer_url,
                "shop_name": history.shop_name,
                "image_url": None,
                "receipt_id": None
            }
            
        # Lógica de limpieza según el tipo de acción
        if history.action_type in ["LINKED_MANUAL", "SMART_MATCH", "UPDATE"]:
            # Borrar la oferta del catálogo para que el item "vuelva" a ser una oportunidad nueva
            offer = db.query(OfferModel).filter(OfferModel.url == history.offer_url).first()
            if offer:
                db.delete(offer)
        
        elif history.action_type == "DISCARDED":
            # Borrar de la lista negra
            bl = db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url == history.offer_url).first()
            if bl:
                db.delete(bl)
        
        # Recrear el item en el Purgatorio
        purgatory_item = PendingMatchModel(
            scraped_name=original_item["scraped_name"],
            ean=original_item.get("ean"),
            price=original_item["price"],
            currency=original_item.get("currency", "EUR"),
            url=original_item["url"],
            shop_name=original_item["shop_name"],
            image_url=original_item.get("image_url"),
            receipt_id=original_item.get("receipt_id")
        )
        db.add(purgatory_item)
        
        # Eliminar la entrada de historial para evitar duplicidad de reversión
        db.delete(history)
        db.commit()
        
        return {"status": "success", "message": f"Justicia restaurada: '{history.product_name}' devuelto al Purgatorio"}

@app.post("/api/scrapers/run", dependencies=[Depends(verify_api_key)])
async def run_scrapers(request: ScraperRunRequest, background_tasks: BackgroundTasks):
    """Inicia la recolección de reliquias en segundo plano (Admin Only)"""
    background_tasks.add_task(run_scraper_task, request.scraper_name, request.trigger_type)
    return {"status": "success", "message": f"Incursión '{request.scraper_name}' ({request.trigger_type}) desplegada en los páramos de Eternia"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.interfaces.api.main:app", host="127.0.0.1", port=8000, reload=True)
