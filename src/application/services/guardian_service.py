
import json
import os
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from src.domain.models import CollectionItemModel, ProductModel
from loguru import logger

class GuardianService:
    @staticmethod
    def backup_stock(db: Session, backup_dir: str = "data/backups") -> str:
        """
        Creates a time-stamped JSON backup of the collection_items table.
        Returns the path to the backup file.
        """
        try:
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path(backup_dir) / f"collection_backup_{timestamp}.json"
            
            # Fetch all collection items with basic product info for context
            items = db.query(CollectionItemModel).all()
            
            backup_data = []
            for item in items:
                # Safely get product identifier
                product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
                p_name = product.name if product else "Unknown"
                f_id = product.figure_id if product else "Unknown"
                
                backup_data.append({
                    "product_id": item.product_id,
                    "product_name": p_name,
                    "figure_id": f_id,
                    "owner_id": item.owner_id,
                    "acquired": item.acquired,
                    "condition": item.condition,
                    "purchase_price": item.purchase_price,
                    "notes": item.notes,
                    "acquired_at": item.acquired_at.isoformat() if item.acquired_at else None
                })
            
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🛡️ Guardian: Pre-flight backup created at {backup_path} ({len(backup_data)} items)")
            return str(backup_path)
        except Exception as e:
            logger.error(f"🛡️ Guardian: Failed to create backup: {e}")
            raise

    @staticmethod
    def restore_from_json(db: Session, json_path: str):
        """
        Emergency restoration of collection items from a JSON backup.
        """
        if not os.path.exists(json_path):
            logger.error(f"🛡️ Guardian: Backup file not found: {json_path}")
            return False
            
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            restored_count = 0
            for entry in data:
                # Find product by figure_id (more robust than internal ID across purges)
                f_id = entry.get("figure_id")
                if not f_id or f_id == "Unknown": continue
                
                product = db.query(ProductModel).filter(ProductModel.figure_id == f_id).first()
                if not product:
                    logger.warning(f"🛡️ Guardian: Skipping restoration for {f_id} (Product not in catalog)")
                    continue
                
                # Check if already exists
                exists = db.query(CollectionItemModel).filter_by(
                    product_id=product.id,
                    owner_id=entry["owner_id"]
                ).first()
                
                if not exists:
                    item = CollectionItemModel(
                        product_id=product.id,
                        owner_id=entry["owner_id"],
                        acquired=entry["acquired"],
                        condition=entry.get("condition", "New"),
                        purchase_price=entry.get("purchase_price"),
                        notes=f"[RESTORER] {entry.get('notes', '')}",
                        acquired_at=datetime.fromisoformat(entry["acquired_at"]) if entry.get("acquired_at") else datetime.now()
                    )
                    db.add(item)
                    restored_count += 1
            
            db.commit()
            logger.info(f"🛡️ Guardian: Restored {restored_count} collection items from backup.")
            return True
        except Exception as e:
            logger.error(f"🛡️ Guardian: Restoration error: {e}")
            db.rollback()
            return False
