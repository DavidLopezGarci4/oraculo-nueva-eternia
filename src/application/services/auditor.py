import json
import os
from datetime import datetime
from pathlib import Path
from src.infrastructure.repositories.product import ProductRepository

class AuditorService:
    def __init__(self, product_repo: ProductRepository):
        self.repo = product_repo
        self.receipts_dir = Path("vec3/var/receipts")
        self.receipts_dir.mkdir(parents=True, exist_ok=True)

    def log_offer_event(self, action_type: str, offer_data: dict, details: str = None):
        # Enriquecer detalles con JSON para permitir reversión futura para cualquier tipo de acción
        import json
        history_details = {
            "info": details,
            "original_item": {
                "scraped_name": offer_data.get("name"),
                "ean": offer_data.get("ean"),
                "price": offer_data.get("price"),
                "currency": offer_data.get("currency", "EUR"),
                "url": offer_data.get("url"),
                "shop_name": offer_data.get("shop_name"),
                "image_url": offer_data.get("image_url"),
                "receipt_id": offer_data.get("receipt_id")
            }
        }

        self.repo.add_to_history(
            action_type=action_type,
            offer_url=offer_data["url"],
            product_name=offer_data["name"],
            shop_name=offer_data["shop_name"],
            price=offer_data["price"],
            details=json.dumps(history_details)
        )

        receipt = {
            "timestamp": datetime.utcnow().isoformat(),
            "actor": "AuditorService",
            "action": action_type,
            "offer_url": offer_data["url"],
            "status": "LOGGED"
        }
        
        filename = f"event_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}.json"
        with open(self.receipts_dir / filename, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2)

        return receipt
