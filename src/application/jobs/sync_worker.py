
import json
import requests
import time
from loguru import logger
from src.infrastructure.database import SessionLocal
from src.infrastructure.repositories.sync_queue import SyncQueueRepository

class SyncWorker:
    def __init__(self, broker_url: str = "http://127.0.0.1:8000"):
        self.broker_url = broker_url

    def process_queue(self):
        """Procesa un lote de la cola de sincronización."""
        with SessionLocal() as db:
            repo = SyncQueueRepository(db)
            pending = repo.get_pending(limit=20)
            
            if not pending:
                return 0

            logger.info(f"Worker :: Found {len(pending)} pending actions. Syncing...")
            
            # Preparar Batch
            batch = []
            for item in pending:
                batch.append({
                    "action_type": item.action_type,
                    "payload": json.loads(item.payload)
                })
            
            try:
                # Enviar al Broker
                response = requests.post(f"{self.broker_url}/sync/batch", json=batch, timeout=10)
                
                if response.status_code == 200:
                    # Marcar como sincronizados
                    for item in pending:
                        repo.mark_synced(item.id)
                    logger.success(f"Worker :: Successfully synced {len(pending)} items.")
                    return len(pending)
                else:
                    logger.error(f"Worker :: Broker returned error {response.status_code}")
                    for item in pending:
                        repo.mark_failed(item.id, f"HTTP {response.status_code}")
                    return 0
            except Exception as e:
                logger.error(f"Worker :: Connection error: {e}")
                for item in pending:
                    repo.mark_failed(item.id, str(e))
                return 0

if __name__ == "__main__":
    worker = SyncWorker()
    while True:
        synced = worker.process_queue()
        if synced == 0:
            time.sleep(10) # Wait for more work
        else:
            time.sleep(1) # Continue processing if queue was full
