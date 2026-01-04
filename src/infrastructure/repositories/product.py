from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from src.infrastructure.repositories.base import BaseRepository
from src.domain.models import ProductModel, OfferModel, PendingMatchModel, OfferHistoryModel

class ProductRepository(BaseRepository[ProductModel]):
    def __init__(self, db: Session):
        super().__init__(ProductModel, db)

    def get_by_name(self, name: str) -> Optional[ProductModel]:
        return self.db.query(ProductModel).filter(ProductModel.name == name).first()

    def get_by_figure_id(self, figure_id: str) -> Optional[ProductModel]:
        return self.db.query(ProductModel).filter(ProductModel.figure_id == figure_id).first()

    def get_by_series(self, series: str) -> List[ProductModel]:
        return self.db.query(ProductModel).filter(ProductModel.sub_category == series).all()

    def get_offer_by_url(self, url: str) -> Optional[OfferModel]:
        return self.db.query(OfferModel).filter(OfferModel.url == url).first()
    
    def add_offer(self, product: ProductModel, offer_data: dict, commit: bool = True) -> tuple[OfferModel, Optional[float]]:
        from src.domain.models import PriceHistoryModel
        
        target_url = offer_data["url"]
        existing_offer = next((o for o in product.offers if o.url == target_url), None)
        current_price = float(offer_data["price"])
        alert_discount = None
        
        # --- EAN KAIZEN: Update product EAN if missing ---
        if not product.ean and offer_data.get("ean"):
             product.ean = offer_data["ean"]
             self.db.add(product)
        
        if existing_offer:
            # Check for Price Changes
            if abs(existing_offer.price - current_price) > 0.01:
                 ph = PriceHistoryModel(offer_id=existing_offer.id, price=current_price)
                 self.db.add(ph)

            # Check for Alert Condition (New Low + Significant Discount)
            if existing_offer.min_price > 0 and current_price < existing_offer.min_price:
                 if existing_offer.max_price > 0:
                     discount = 1.0 - (current_price / existing_offer.max_price)
                     if discount >= 0.20:
                         alert_discount = discount

            # Update Stats
            if existing_offer.min_price == 0 or current_price < existing_offer.min_price:
                existing_offer.min_price = current_price
            
            if current_price > existing_offer.max_price:
                existing_offer.max_price = current_price
                
            existing_offer.price = current_price
            existing_offer.is_available = offer_data.get("is_available", True)
            existing_offer.last_seen = datetime.utcnow()
            
            # --- 3OX: Update Audit Receipt ---
            if "receipt_id" in offer_data:
                existing_offer.receipt_id = offer_data["receipt_id"]
            
            self.db.add(existing_offer)
            if commit:
                self.db.commit()
                self.db.refresh(existing_offer)
            else:
                self.db.flush()
            return existing_offer, alert_discount
        else:
            # Create new Offer
            new_offer = OfferModel(
                product_id=product.id,
                shop_name=offer_data["shop_name"],
                price=current_price,
                currency=offer_data.get("currency", "EUR"),
                url=offer_data["url"],
                is_available=offer_data.get("is_available", True),
                min_price=current_price,
                max_price=current_price,
                receipt_id=offer_data.get("receipt_id") # --- 3OX Audit ---
            )
            self.db.add(new_offer)
            self.db.flush() 
            
            # Initial History
            ph = PriceHistoryModel(offer_id=new_offer.id, price=current_price)
            self.db.add(ph)
            
            if commit:
                self.db.commit()
                self.db.refresh(new_offer)
            else:
                self.db.flush()
            return new_offer, None

    def get_active_deals(self, min_discount: float = 0.20, max_original_price: float = None):
        """
        Find offers where current price is lower than max_price by at least min_discount.
        """
        from sqlalchemy import desc
        
        query = self.db.query(OfferModel).join(ProductModel).filter(
            OfferModel.is_available == True,
            OfferModel.max_price > 0,
            OfferModel.price < (OfferModel.max_price * (1 - min_discount))
        )
        
        if max_original_price is not None:
             query = query.filter(OfferModel.max_price <= max_original_price)
        
        offers = query.order_by(desc(OfferModel.last_seen)).all()
        
        deduped = {}
        for o in offers:
            key = (o.product_id, o.shop_name)
            if key not in deduped:
                discount = 1 - (o.price / o.max_price)
                deduped[key] = (o.product, o, discount)
        
        results = list(deduped.values())
        results.sort(key=lambda x: x[2], reverse=True)
        return results

    # --- Purgatorio & Audit Methods ---
    def get_pending_matches(self) -> List[PendingMatchModel]:
        return self.db.query(PendingMatchModel).all()

    def add_to_history(self, action_type: str, offer_url: str, product_name: str, shop_name: str, price: float, details: str = None):
        history = OfferHistoryModel(
            action_type=action_type,
            offer_url=offer_url,
            product_name=product_name,
            shop_name=shop_name,
            price=price,
            details=details
        )
        self.db.add(history)
        self.db.commit()
