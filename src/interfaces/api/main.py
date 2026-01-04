
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from loguru import logger

app = FastAPI(title="Oráculo API Broker", version="1.0.0")

class SyncAction(BaseModel):
    action_type: str
    payload: dict

@app.get("/health")
def health():
    return {"status": "ok", "message": "Eternia is online"}

@app.post("/sync/batch")
async def sync_batch(actions: List[SyncAction]):
    """
    Recibe un lote de acciones desde el worker local.
    En el futuro, esto escribirá en Supabase/Postgres.
    """
    logger.info(f"Received sync batch with {len(actions)} actions.")
    # TODO: Integrar con Repositorio Postgres/Supabase
    return {"status": "success", "synced_count": len(actions)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
