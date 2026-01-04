
from sqlalchemy.orm import Session
from src.domain.models import SyncQueueModel
import json
from datetime import datetime

class SyncQueueRepository:
    def __init__(self, db: Session):
        self.db = db

    def push(self, action_type: str, payload: dict):
        """Añade una acción a la cola local."""
        item = SyncQueueModel(
            action_type=action_type,
            payload=json.dumps(payload),
            status="PENDING"
        )
        self.db.add(item)
        return item

    def get_pending(self, limit: int = 10):
        """Obtiene acciones pendientes para el worker."""
        return self.db.query(SyncQueueModel).filter(
            SyncQueueModel.status == "PENDING"
        ).order_by(SyncQueueModel.created_at.asc()).limit(limit).all()

    def mark_synced(self, item_id: int):
        """Marca un item como sincronizado exitosamente."""
        item = self.db.query(SyncQueueModel).get(item_id)
        if item:
            item.status = "SYNCED"
            item.synced_at = datetime.utcnow()
            self.db.commit()

    def mark_failed(self, item_id: int, error: str):
        """Registra un fallo en la sincronización."""
        item = self.db.query(SyncQueueModel).get(item_id)
        if item:
            item.status = "FAILED"
            item.retry_count += 1
            item.error_msg = error
            self.db.commit()
