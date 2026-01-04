from sqlalchemy.orm import Session
from src.infrastructure.repositories.product import ProductRepository
from src.application.services.auditor import AuditorService
from src.application.services.sentinel import SentinelService
from src.domain.models import PendingMatchModel, BlackcludedItemModel

class MatchService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)
        self.auditor = AuditorService(self.repo)
        self.sentinel = SentinelService(self.repo)

    def match_item(self, pending_id: int, product_id: int):
        item = self.db.query(PendingMatchModel).filter(PendingMatchModel.id == pending_id).first()
        product = self.repo.get(product_id)

        if not item or not product:
            return False, "Item o Producto no encontrado"

        offer_data = {
            "shop_name": item.shop_name,
            "price": item.price,
            "currency": item.currency,
            "url": item.url,
            "is_available": True,
            "name": product.name,
            "ean": item.ean
        }
        
        offer, discount = self.repo.add_offer(product, offer_data, commit=False)
        self.auditor.log_offer_event("LINKED_MANUAL", offer_data, details=f"Matched to product ID {product_id}")
        self.sentinel.check_alerts(product.id, item.price)
        self.db.delete(item)
        self.db.commit()
        return True, "Item vinculado con éxito"

    def discard_item(self, pending_id: int, reason: str = "manual_discard"):
        item = self.db.query(PendingMatchModel).filter(PendingMatchModel.id == pending_id).first()
        if not item:
            return False, "Item no encontrado"

        bl = BlackcludedItemModel(
            url=item.url,
            scraped_name=item.scraped_name,
            reason=reason
        )
        self.db.add(bl)
        offer_data = {
            "url": item.url,
            "name": item.scraped_name,
            "shop_name": item.shop_name,
            "price": item.price
        }
        self.auditor.log_offer_event("DISCARDED", offer_data, details=reason)
        self.db.delete(item)
        self.db.commit()
        return True, "Item descartado con éxito"
