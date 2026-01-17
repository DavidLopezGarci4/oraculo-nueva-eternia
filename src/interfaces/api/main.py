from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from loguru import logger
from src.core.config import settings
from src.infrastructure.database_cloud import SessionCloud

from datetime import datetime
app = FastAPI(title="Oráculo API Broker", version="1.0.0")

# Configurar CORS para permitir peticiones universales (Útil para acceso móvil y Docker)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permitimos todo para facilitar el acceso desde cualquier IP del hogar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.ORACULO_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key. Access Denied.")
    return x_api_key

from pydantic import BaseModel, ConfigDict
# ... (existing imports will be handled by context if not explicit, but here I replace the class definition part)

class SyncAction(BaseModel):
    action_type: str
    payload: dict

class ProductOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ean: str | None
    image_url: str | None
    category: str
    sub_category: str
    figure_id: str
    variant_name: str | None

    # Financial & Intelligence (Computed)
    purchase_price: float = 0.0
    market_value: float = 0.0
    is_grail: bool = False
    grail_score: float = 0.0
    is_wish: bool = False
    acquired_at: str | None = None

from fastapi import BackgroundTasks
from src.infrastructure.scrapers.harvester import run_harvester
from src.domain.models import ProductModel, PendingMatchModel, ScraperStatusModel, BlackcludedItemModel, OfferModel, ScraperExecutionLogModel, CollectionItemModel, OfferHistoryModel
import json
from sqlalchemy import select

class CollectionToggleRequest(BaseModel):
    product_id: int
    user_id: int
    wish: bool = False

class PurgatoryMatchRequest(BaseModel):
    pending_id: int
    product_id: int

class PurgatoryDiscardRequest(BaseModel):
    pending_id: int
    reason: str = "manual_discard"

class PurgatoryBulkDiscardRequest(BaseModel):
    pending_ids: List[int]
    reason: str = "manual_bulk_discard"

class ScraperRunRequest(BaseModel):
    scraper_name: str = "harvester"  # "harvester", "all", or individual spider name
    trigger_type: str = "manual"

class ProductEditRequest(BaseModel):
    name: str | None = None
    ean: str | None = None
    image_url: str | None = None
    category: str | None = None
    sub_category: str | None = None
    retail_price: float | None = None

class ProductMergeRequest(BaseModel):
    source_id: int
    target_id: int     # "manual" or "scheduled"

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

@app.get("/api/auth/users")
async def get_users():
    """Retorna la lista de usuarios disponibles (Modo Test)"""
    from src.domain.models import UserModel
    with SessionCloud() as db:
        users = db.query(UserModel).all()
        return [{"id": u.id, "username": u.username, "role": u.role} for u in users]

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
    from src.domain.models import CollectionItemModel, OfferModel
    from sqlalchemy import func
    
    with SessionCloud() as db:
        # 1. Fetch Products + Collection Data
        query = (
            select(ProductModel, CollectionItemModel)
            .join(CollectionItemModel, ProductModel.id == CollectionItemModel.product_id)
            .where(CollectionItemModel.owner_id == user_id)
        )
        results = db.execute(query).all()
        
        if not results:
            return []

        # 2. Bulk Fetch Best Offers to avoid N+1
        product_ids = [p.id for p, c in results]
        
        best_price_query = (
            select(OfferModel.product_id, func.min(OfferModel.price))
            .where(OfferModel.product_id.in_(product_ids))
            .where(OfferModel.is_available == True)
            .group_by(OfferModel.product_id)
        )
        best_prices = dict(db.execute(best_price_query).all()) # {pid: min_price}

        # 3. Construct Response with Grail & Wish Logic
        output_list = []
        for product, collection_item in results:
            market_val = best_prices.get(product.id, 0.0)
            
            # Smart Grail Logic
            is_grail = False
            grail_score = 0.0
            if market_val > 0 and product.retail_price and product.retail_price > 0:
                roi = ((market_val - product.retail_price) / product.retail_price) * 100
                if roi > 200: 
                    is_grail = True
                    grail_score = min(roi / 10, 100)

            output_list.append(ProductOutput(
                id=product.id,
                name=product.name,
                ean=product.ean,
                image_url=product.image_url,
                category=product.category,
                sub_category=product.sub_category,
                figure_id=product.figure_id,
                variant_name=product.variant_name,
                purchase_price=collection_item.purchase_price or 0.0,
                market_value=market_val,
                is_grail=is_grail,
                grail_score=grail_score,
                is_wish=not collection_item.acquired,
                acquired_at=collection_item.acquired_at.isoformat() if collection_item.acquired_at else None
            ))
        
        return output_list

@app.put("/api/products/{product_id}", dependencies=[Depends(verify_api_key)])
async def edit_product(product_id: int, request: ProductEditRequest):
    """
    Actualiza metadatos de un producto (Editor de la Verdad).
    """
    with SessionCloud() as db:
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        if request.name is not None: product.name = request.name
        if request.ean is not None: product.ean = request.ean
        if request.image_url is not None: product.image_url = request.image_url
        if request.category is not None: product.category = request.category
        if request.sub_category is not None: product.sub_category = request.sub_category
        if request.retail_price is not None: product.retail_price = request.retail_price
        
        db.commit()
        return {"status": "success", "message": f"Reliquia '{product.name}' actualizada con éxito"}

@app.get("/api/admin/duplicates", dependencies=[Depends(verify_api_key)])
async def get_duplicates():
    """
    Detecta posibles duplicados basados en EAN (Exacto).
    """
    with SessionCloud() as db:
        products = db.query(ProductModel).all()
        duplicates = []
        
        # Exact EAN Match
        ean_map = {}
        for p in products:
            if p.ean:
                if p.ean in ean_map:
                    ean_map[p.ean].append({
                        "id": p.id,
                        "name": p.name,
                        "image_url": p.image_url,
                        "sub_category": p.sub_category,
                        "figure_id": p.figure_id
                    })
                else:
                    ean_map[p.ean] = [{
                        "id": p.id,
                        "name": p.name,
                        "image_url": p.image_url,
                        "sub_category": p.sub_category,
                        "figure_id": p.figure_id
                    }]
        
        for ean, prods in ean_map.items():
            if len(prods) > 1:
                duplicates.append({
                    "reason": f"EAN compartido: {ean}",
                    "products": prods
                })
        
        return duplicates

@app.post("/api/products/merge", dependencies=[Depends(verify_api_key)])
async def merge_products(request: ProductMergeRequest):
    """
    Fusiona dos productos. Transfiere ofertas y colecciones al target y borra el source.
    """
    with SessionCloud() as db:
        source = db.query(ProductModel).filter(ProductModel.id == request.source_id).first()
        target = db.query(ProductModel).filter(ProductModel.id == request.target_id).first()
        if not source or not target: raise HTTPException(status_code=404, detail="Producto(s) no encontrado")
            
        # 1. Transferir ofertas
        db.query(OfferModel).filter(OfferModel.product_id == source.id).update({"product_id": target.id})
        
        # 2. Transferir coleccionistas
        source_items = db.query(CollectionItemModel).filter(CollectionItemModel.product_id == source.id).all()
        for item in source_items:
            exists = db.query(CollectionItemModel).filter(
                CollectionItemModel.product_id == target.id,
                CollectionItemModel.owner_id == item.owner_id
            ).first()
            if not exists:
                item.product_id = target.id
            else:
                db.delete(item)
                
        # 3. Eliminar fuente
        source_name = source.name
        db.delete(source)
        db.commit()
        return {"status": "success", "message": f"Fusión divina: '{source_name}' ha sido absorbido por '{target.name}'"}
        
        # 3. Construct Response with Grail Logic
        output_list = []
        for product, item in results:
            # Base data from product
            p_out = ProductOutput.model_validate(product)
            
            # Financial Data
            invested = item.purchase_price if item.purchase_price is not None else (product.retail_price or 0.0)
            market = best_prices.get(product.id, 0.0)
            
            p_out.purchase_price = invested
            p_out.market_value = market
            
            # Grail Detection Logic (Rule: ROI > 50% OR Value > 150€)
            roi = 0.0
            is_grail = False
            
            if invested > 0:
                roi_val = (market - invested) / invested
                roi = round(roi_val * 100, 1)
                
                # Rule 1: ROI > 50% (and confirmed match exists)
                if market > 0 and roi > 50.0:
                    is_grail = True
            
            # Rule 2: High Value Absolute (> 150€)
            if market > 150.0:
                is_grail = True
                
            p_out.is_grail = is_grail
            p_out.grail_score = roi
            
            output_list.append(p_out)
            
        return output_list

@app.post("/api/collection/toggle")
async def toggle_collection(request: CollectionToggleRequest):
    """
    Añade o elimina un producto de la colección del usuario (o lista de deseos).
    """
    from src.domain.models import CollectionItemModel
    with SessionCloud() as db:
        # Buscar si ya existe
        item = db.query(CollectionItemModel).filter(
            CollectionItemModel.product_id == request.product_id,
            CollectionItemModel.owner_id == request.user_id
        ).first()

        if item:
            # Caso 1: Estaba en deseos y ahora lo marcamos como poseído (Upgrade)
            if not item.acquired and not request.wish:
                item.acquired = True
                action = "upgraded"
            # Caso 2: Estaba poseído y ahora lo marcamos como deseos (Downgrade - opcional, por ahora tratamos como toggle normal)
            # Por simplicidad, si ya existe y pulsas lo mismo, se borra (toggle off)
            else:
                db.delete(item)
                action = "removed"
        else:
            # Crear según el tipo solicitado
            new_item = CollectionItemModel(
                product_id=request.product_id,
                owner_id=request.user_id,
                acquired=not request.wish
            )
            db.add(new_item)
            action = "added_wish" if request.wish else "added_owned"
        
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

@app.post("/api/purgatory/discard/bulk", dependencies=[Depends(verify_api_key)])
async def discard_purgatory_bulk(request: PurgatoryBulkDiscardRequest):
    """
    Descarta múltiples items del Purgatorio a la vez.
    """
    with SessionCloud() as db:
        items = db.query(PendingMatchModel).filter(PendingMatchModel.id.in_(request.pending_ids)).all()
        count = 0
        for item in items:
            # Añadir a lista negra para no volver a verlo
            blacklist = BlackcludedItemModel(
                scraped_name=item.scraped_name,
                shop_name=item.shop_name,
                reason=request.reason
            )
            db.add(blacklist)
            db.delete(item)
            count += 1
        
        db.commit()
    
    return {"status": "success", "message": f"{count} items desterrados al abismo."}

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
async def get_dashboard_stats(user_id: int = 1):
    """
    Retorna métricas globales para el Tablero de Inteligencia, filtradas por usuario.
    Diferencia entre items poseídos y lista de deseos.
    """
    try:
        from sqlalchemy import func
        with SessionCloud() as db:
            total_products = db.query(ProductModel).count()
            # Solo contamos items poseídos (acquired=True) para las métricas de "Poder"
            owned_count = db.query(CollectionItemModel).filter(
                CollectionItemModel.owner_id == user_id, 
                CollectionItemModel.acquired == True
            ).count()
            
            wish_count = db.query(CollectionItemModel).filter(
                CollectionItemModel.owner_id == user_id, 
                CollectionItemModel.acquired == False
            ).count()

            # --- FINANCIAL ENGINE (PHASE 6) ---
            total_invested = 0.0
            market_value = 0.0
            
            try:
                # Get best prices map
                all_prices = db.query(OfferModel.product_id, OfferModel.price)\
                    .filter(OfferModel.is_available == True, OfferModel.product_id.isnot(None))\
                    .all()
                    
                best_price_map = {}
                for row in all_prices:
                    pid, price = row
                    if pid is None or price is None: continue
                    if pid not in best_price_map or price < best_price_map[pid]:
                        best_price_map[pid] = price
                        
                # Calcular Inversión y Valor de Mercado (SOLO POSEÍDOS)
                collection_items = db.query(CollectionItemModel).filter(
                    CollectionItemModel.owner_id == user_id,
                    CollectionItemModel.acquired == True
                ).all()
                
                for item in collection_items:
                    total_invested += (item.purchase_price or 0.0)
                    if item.product_id in best_price_map:
                        market_value += best_price_map[item.product_id]
                
                profit_loss = market_value - total_invested
                roi = (profit_loss / total_invested * 100) if total_invested > 0 else 0.0
                
            except Exception as e:
                logger.error(f"Financial Engine Error: {e}")
                market_value = 0.0
                total_invested = 0.0
                profit_loss = 0.0
                roi = 0.0

            # Distribución por tienda (Global, para inteligencia de mercado)
            shop_dist = db.query(OfferModel.shop_name, func.count(OfferModel.id))\
                .filter(OfferModel.product_id.isnot(None), OfferModel.is_available == True)\
                .group_by(OfferModel.shop_name)\
                .all()
            
            match_count = sum(count for _, count in shop_dist)
            
            return {
                "total_products": total_products,
                "owned_count": owned_count,
                "wish_count": wish_count,
                "financial": {
                    "total_invested": round(total_invested, 2),
                    "market_value": round(market_value, 2),
                    "profit_loss": round(profit_loss, 2),
                    "roi": round(roi, 1)
                },
                "match_count": match_count,
                "shop_distribution": [{"shop": s, "count": c} for s, c in shop_dist]
            }
    except Exception as e:
        logger.error(f"CRITICAL DASHBOARD ERROR: {e}")
        return {
            "total_products": 0, "owned_count": 0, "wish_count": 0,
            "financial": {"total_invested": 0, "market_value": 0, "profit_loss": 0, "roi": 0},
            "match_count": 0, "shop_distribution": []
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

@app.get("/api/products/{product_id}/price-history")
async def get_product_price_history(product_id: int):
    """
    Retorna la evolución de precios de un producto agrupada por tienda.
    Fase 8.3: Cronos.
    """
    from src.domain.models import OfferModel, PriceHistoryModel
    
    with SessionCloud() as db:
        # Buscamos todas las ofertas vinculadas a este producto
        offers = db.query(OfferModel).filter(OfferModel.product_id == product_id).all()
        
        results = []
        for offer in offers:
            # Para cada oferta (tienda), obtener su historial de precios
            history = db.query(PriceHistoryModel)\
                .filter(PriceHistoryModel.offer_id == offer.id)\
                .order_by(PriceHistoryModel.recorded_at.asc())\
                .all()
            
            if history:
                results.append({
                    "shop_name": offer.shop_name,
                    "history": [
                        {
                            "date": h.recorded_at.isoformat(),
                            "price": h.price
                        } for h in history
                    ]
                })
        
        return results

@app.get("/api/dashboard/hall-of-fame")
async def get_dashboard_hall_of_fame(user_id: int = 1):
    """
    Fase 6.3: Retorna los 'Griales del Reino' (Top Valor) y 'Potencial Oculto' (Top ROI).
    """
    from src.domain.models import CollectionItemModel, OfferModel, ProductModel
    from sqlalchemy import func
    
    with SessionCloud() as db:
        # 1. Obtener todos los items de colección filtrados por el usuario
        items = (
            db.query(CollectionItemModel)
            .join(ProductModel)
            .filter(CollectionItemModel.acquired == True, CollectionItemModel.owner_id == user_id)
            .all()
        )
        
        if not items:
            return {"top_value": [], "top_roi": []}
            
        # 2. Obtener mejores precios actuales
        product_ids = [item.product_id for item in items]
        best_price_query = (
            select(OfferModel.product_id, func.min(OfferModel.price))
            .where(OfferModel.product_id.in_(product_ids))
            .where(OfferModel.is_available == True)
            .group_by(OfferModel.product_id)
        )
        best_prices = dict(db.execute(best_price_query).all())
        
        # 3. Calcular métricas para cada item
        analyzed_items = []
        for item in items:
            market = best_prices.get(item.product_id, 0.0)
            invested = item.purchase_price if item.purchase_price is not None else 0.0
            
            roi = 0.0
            if invested > 0 and market > 0:
                roi = ((market - invested) / invested) * 100
            
            analyzed_items.append({
                "id": item.product.id,
                "name": item.product.name,
                "image_url": item.product.image_url,
                "market_value": round(market, 2),
                "invested_value": round(invested, 2),
                "roi_percentage": round(roi, 1)
            })
            
        # 4. Ordenar y filtrar
        # Top Value (Solo si tienen valor de mercado)
        top_value = sorted(
            [x for x in analyzed_items if x["market_value"] > 0], 
            key=lambda x: x["market_value"], 
            reverse=True
        )[:3]
        
        # Top ROI (Solo si hay ganancia real y valoración de mercado)
        top_roi = sorted(
            [x for x in analyzed_items if x["market_value"] > 0 and x["roi_percentage"] > 0],
            key=lambda x: x["roi_percentage"],
            reverse=True
        )[:3]
        
        return {
            "top_value": top_value,
            "top_roi": top_roi
        }

@app.get("/api/dashboard/top-deals")
async def get_top_deals(user_id: int = 2):
    """
    Retorna las 20 mejores ofertas actuales de items NO CAPTURADOS.
    MEJORA: Solo muestra el mejor precio por producto (sin duplicados).
    """
    from sqlalchemy import func, and_
    
    with SessionCloud() as db:
        # 1. Obtenemos IDs de productos ya capturados por el usuario
        owned_ids = [p[0] for p in db.query(CollectionItemModel.product_id).filter(CollectionItemModel.owner_id == user_id).all()]

        # 2. Subquery: Encontrar el precio mínimo para cada producto disponible
        best_prices_subq = db.query(
            OfferModel.product_id,
            func.min(OfferModel.price).label('min_price')
        ).filter(
            OfferModel.is_available == True,
            OfferModel.product_id.notin_(owned_ids) if owned_ids else True
        ).group_by(OfferModel.product_id).subquery()

        # 3. Join para obtener los detalles de la oferta más barata por producto
        offers = db.query(OfferModel).join(
            best_prices_subq,
            and_(
                OfferModel.product_id == best_prices_subq.c.product_id,
                OfferModel.price == best_prices_subq.c.min_price
            )
        ).join(ProductModel).filter(
            OfferModel.is_available == True
        ).order_by(OfferModel.price.asc()).limit(20).all()
        
        # 4. Deduplicar por product_id en Python (failsafe para empates de precio)
        seen_product_ids = set()
        unique_offers = []
        for o in offers:
            if o.product_id not in seen_product_ids:
                seen_product_ids.add(o.product_id)
                unique_offers.append(o)
        
        return [
            {
                "id": o.id,
                "product_name": o.product.name,
                "price": o.price,
                "shop_name": o.shop_name,
                "url": o.url,
                "image_url": o.product.image_url
            } for o in unique_offers[:20]  # Garantizar máximo 20
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
            "timestamp": h.timestamp.isoformat(),
            "offer_url": h.offer_url
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

# === WALLAPOP EXTENSION IMPORT ===
class WallapopProduct(BaseModel):
    title: str
    price: float
    url: str
    imageUrl: str | None = None

class WallapopImportRequest(BaseModel):
    products: List[WallapopProduct]

@app.get("/api/health")
def api_health():
    """Health check para la extensión de Chrome"""
    return {"status": "ok", "service": "oraculo", "version": "1.0.0"}

@app.post("/api/wallapop/import")
async def import_wallapop_products(request: WallapopImportRequest):
    """
    Recibe productos de Wallapop desde la extensión de Chrome
    y los guarda en el Purgatorio para revisión manual.
    """
    imported = 0
    
    with SessionCloud() as db:
        for product in request.products:
            # Verificar si ya existe
            existing = db.query(PendingMatchModel).filter(
                PendingMatchModel.url == product.url
            ).first()
            
            if existing:
                continue
            
            # Crear item en Purgatorio
            pending = PendingMatchModel(
                scraped_name=f"[Wallapop] {product.title}",
                price=product.price,
                currency="EUR",
                url=product.url,
                shop_name="Wallapop",
                image_url=product.imageUrl,
                found_at=datetime.utcnow()
            )
            db.add(pending)
            imported += 1
        
        db.commit()
    
    logger.info(f"[Wallapop Extension] Importados {imported} productos al Purgatorio")
    return {"status": "success", "imported": imported, "total_received": len(request.products)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.interfaces.api.main:app", host="127.0.0.1", port=8000, reload=True)
