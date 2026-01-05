from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from loguru import logger
from src.core.config import settings

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

@app.get("/health")
def health():
    return {"status": "ok", "message": "Eternia is online"}

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel, PendingMatchModel
import json
from sqlalchemy import select

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
                    # Aquí la lógica para actualizar Postgres
                    # (En un paso siguiente crearemos un repositorio de dominio cloud)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
