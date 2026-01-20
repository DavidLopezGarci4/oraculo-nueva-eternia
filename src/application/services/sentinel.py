import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from src.infrastructure.repositories.product import ProductRepository
from src.domain.models import PriceAlertModel, ProductModel, OfferModel, PendingMatchModel

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

    def validate_cross_reference(self, product: ProductModel, price: float, image_url: Optional[str] = None) -> Tuple[bool, str, List[str]]:
        """
        Realiza la validación cruzada del item.
        Retorna (is_blocked, status, flags)
        """
        is_blocked = False
        status = "VALIDATED"
        flags = []

        # 1. Validación de Precio (Desviación > 40%)
        if product.avg_market_price and product.avg_market_price > 0:
            deviation = abs(price - product.avg_market_price) / product.avg_market_price
            if deviation > 0.40:
                is_blocked = True
                status = "PENDING"
                flags.append("Alerta de Anomalía: Desviación de precio >40%")

        # 2. Validación Visual (Comparación de Hash)
        # Nota: En esta fase, si el hash maestro existe y la imagen del scraper no coincide, bloqueamos.
        # Por ahora simulamos la obtención del hash de la imagen del scraper.
        if product.master_image_hash and image_url:
            # TODO: Implement actual image hashing logic (e.g. using imagehash library)
            # Por ahora, si tenemos master_image_hash pero no hay una lógica de hashing activa,
            # marcamos como advertencia si la URL es muy distinta (fallback simple)
            pass

        if is_blocked and any("Anomalía" in f for f in flags):
            # Si solo es precio, el status puede ser PENDING para revisión
            pass
        
        if "Bootleg" in str(flags): # Placeholder para lógica futura
            status = "PENDING"
            is_blocked = True

        return is_blocked, status, flags
