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
        self.repo.add_to_history(
            action_type=action_type,
            offer_url=offer_data["url"],
            product_name=offer_data["name"],
            shop_name=offer_data["shop_name"],
            price=offer_data["price"],
            details=details
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
