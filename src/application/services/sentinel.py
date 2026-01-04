from datetime import datetime
from src.infrastructure.repositories.product import ProductRepository
from src.domain.models import PriceAlertModel

class SentinelService:
    def __init__(self, product_repo: ProductRepository):
        self.repo = product_repo

    def check_alerts(self, product_id: int, current_price: float):
        alerts = self.repo.db.query(PriceAlertModel).filter(
            PriceAlertModel.product_id == product_id,
            PriceAlertModel.is_active == True,
            PriceAlertModel.target_price >= current_price
        ).all()

        triggered = []
        for alert in alerts:
            alert.last_notified_at = datetime.utcnow()
            self.repo.db.add(alert)
            triggered.append(alert)
            print(f"[SENTINEL] ALERT TRIGGERED: Product {product_id} at {current_price} EUR (Target: {alert.target_price} EUR)")
        
        if triggered:
            self.repo.db.commit()
            
        return triggered
