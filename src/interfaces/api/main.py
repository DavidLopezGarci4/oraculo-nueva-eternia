from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from loguru import logger
from src.core.config import settings
from src.infrastructure.database_cloud import SessionCloud

app = FastAPI(title="Oráculo API Broker", version="1.0.0")

# Configurar CORS para permitir peticiones desde el frontend (Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
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
from src.domain.models import ProductModel, PendingMatchModel, ScraperStatusModel, BlackcludedItemModel, OfferModel
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
    """Retorna items en el Purgatorio (PendingMatchModel)"""
    with SessionCloud() as db:
        items = db.query(PendingMatchModel).all()
        return items

@app.post("/api/purgatory/match")
async def match_purgatory(request: PurgatoryMatchRequest):
    """Vincula un item del Purgatorio con un Producto existente"""
    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == request.pending_id).first()
        product = db.query(ProductModel).filter(ProductModel.id == request.product_id).first()
        
        if not item or not product:
            raise HTTPException(status_code=404, detail="Reliquia o Producto no encontrado")
        
        new_offer = OfferModel(
            product_id=product.id,
            shop_name=item.shop_name,
            price=item.price,
            currency=item.currency,
            url=item.url,
            is_available=True
        )
        db.add(new_offer)
        db.delete(item)
        db.commit()
        return {"status": "success", "message": "Vínculo sagrado establecido"}

@app.post("/api/purgatory/discard")
async def discard_purgatory(request: PurgatoryDiscardRequest):
    """Descarta un item del Purgatorio y lo añade a la lista negra"""
    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == request.pending_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Reliquia no encontrada")
        
        bl = BlackcludedItemModel(
            url=item.url,
            scraped_name=item.scraped_name,
            reason=request.reason
        )
        db.add(bl)
        db.delete(item)
        db.commit()
        return {"status": "success", "message": "Reliquia desterrada al abismo"}

# --- SCRAPER CONTROL ENDPOINTS ---

def run_scraper_task():
    """Wrapper para ejecutar el harvester y actualizar el estado en BD"""
    from datetime import datetime
    with SessionCloud() as db:
        status = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == "Harvester").first()
        if not status:
            status = ScraperStatusModel(spider_name="Harvester")
            db.add(status)
        status.status = "running"
        status.start_time = datetime.utcnow()
        db.commit()

    try:
        run_harvester()
        with SessionCloud() as db:
            status = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == "Harvester").first()
            status.status = "completed"
            status.end_time = datetime.utcnow()
            db.commit()
    except Exception as e:
        logger.error(f"Scraper Error: {e}")
        with SessionCloud() as db:
            status = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == "Harvester").first()
            status.status = f"error: {str(e)}"
            db.commit()

@app.get("/api/scrapers/status")
async def get_scrapers_status():
    """Retorna el estado actual de los recolectores"""
    with SessionCloud() as db:
        return db.query(ScraperStatusModel).all()

@app.post("/api/scrapers/run")
async def run_scrapers(background_tasks: BackgroundTasks):
    """Inicia la recolección de reliquias en segundo plano"""
    background_tasks.add_task(run_scraper_task)
    return {"status": "success", "message": "Recolectores desplegados en los páramos de Eternia"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.interfaces.api.main:app", host="127.0.0.1", port=8000, reload=True)
