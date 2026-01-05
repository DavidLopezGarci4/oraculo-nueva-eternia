from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List
from loguru import logger
from src.core.config import settings

app = FastAPI(title="Oráculo API Broker", version="1.0.0")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.ORACULO_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key. Access Denied.")
    return x_api_key

class SyncAction(BaseModel):
    action_type: str
    payload: dict

@app.get("/health")
def health():
    return {"status": "ok", "message": "Eternia is online"}

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel, PendingMatchModel
import json

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
