from sqlalchemy.orm import Session
from typing import List, Optional
from src.infrastructure.repositories.base import BaseRepository
from src.domain.models import CollectionItemModel

class CollectionRepository(BaseRepository[CollectionItemModel]):
    def __init__(self, db: Session):
        super().__init__(CollectionItemModel, db)

    def get_by_user(self, user_id: int) -> List[CollectionItemModel]:
        return self.db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == user_id).all()

    def get_item(self, user_id: int, product_id: int) -> Optional[CollectionItemModel]:
        return self.db.query(CollectionItemModel).filter(
            CollectionItemModel.owner_id == user_id,
            CollectionItemModel.product_id == product_id
        ).first()

    def get_collection_summary(self, user_id: int) -> dict:
        items = self.get_by_user(user_id)
        return {
            "total_items": len(items),
            "total_quantity": sum(item.quantity for item in items),
            "total_investment": sum((item.acquisition_price or 0) * item.quantity for item in items)
        }
