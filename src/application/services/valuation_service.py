
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.domain.models import OfferModel, ProductModel, LogisticRuleModel
from src.application.services.logistics_service import LogisticsService
import logging

logger = logging.getLogger("ValuationService")

class ValuationService:
    def __init__(self, db: Session):
        self.db = db
        # Pre-load logistics rules to optimize calculations
        rules = self.db.query(LogisticRuleModel).all()
        self.rules_map = {f"{r.shop_name}_{r.country_code}": r for r in rules}

    def get_consolidated_value(self, product: ProductModel, user_location: str = "ES") -> float:
        """
        Implementation of the VALUATION WATERFALL.
        Returns the best possible market value estimation.
        """
        # --- LEVEL 1: ACTIVE RETAIL OFFER (BEST LANDED) ---
        best_retail = self.db.query(OfferModel).filter(
            OfferModel.product_id == product.id,
            OfferModel.is_available == True,
            OfferModel.source_type == "Retail"
        ).order_by(OfferModel.price.asc()).first()
        
        if best_retail:
            return LogisticsService.optimized_get_landing_price(
                best_retail.price, 
                best_retail.shop_name, 
                user_location, 
                self.rules_map
            )

        # --- LEVEL 2: ACTIVE P2P OFFER (BEST LANDED) ---
        best_p2p = self.db.query(OfferModel).filter(
            OfferModel.product_id == product.id,
            OfferModel.is_available == True,
            OfferModel.source_type == "Peer-to-Peer"
        ).order_by(OfferModel.price.asc()).first()
        
        if best_p2p:
            return LogisticsService.optimized_get_landing_price(
                best_p2p.price, 
                best_p2p.shop_name, 
                user_location, 
                self.rules_map
            )

        # --- LEVEL 3: AF411 HISTORICAL BENCHMARK (ORACULO MASTER) ---
        # Prefer the more granular avg_market_price if populated
        if product.avg_market_price and product.avg_market_price > 0:
            return product.avg_market_price

        # --- LEVEL 4: AF411 SEGREGATED STATS ---
        if product.avg_p2p_price and product.avg_p2p_price > 0:
            return product.avg_p2p_price
        
        if product.avg_retail_price and product.avg_retail_price > 0:
            return product.avg_retail_price

        # --- LEVEL 5: MSRP (THE ABSOLUTE FLOOR) ---
        if product.retail_price and product.retail_price > 0:
            return product.retail_price

        return 0.0

    def get_collection_valuation(self, user_id: int, user_location: str = "ES") -> dict:
        """Calculates total value of a user's collection using the waterfall."""
        from src.domain.models import CollectionItemModel
        
        items = self.db.query(CollectionItemModel).filter(
            CollectionItemModel.owner_id == user_id,
            CollectionItemModel.acquired == True
        ).all()
        
        total_value = 0.0
        total_invested = 0.0
        total_landed_market = 0.0 # Phase 15: New Real Landed Metric
        
        for item in items:
            value = self.get_consolidated_value(item.product, user_location)
            total_value += value
            total_invested += (item.purchase_price or 0.0)
            
            # Real Landed Value (Level 1 or 2 exclusively)
            landed = self.get_pure_landed_value(item.product, user_location)
            total_landed_market += (landed or value)
            
        profit_loss = total_value - total_invested
        roi = (profit_loss / total_invested * 100) if total_invested > 0 else 0.0
        
        return {
            "total_value": round(total_value, 2),
            "total_invested": round(total_invested, 2),
            "landed_market_value": round(total_landed_market, 2),
            "profit_loss": round(profit_loss, 2),
            "roi": round(roi, 1),
            "item_count": len(items)
        }

    def get_pure_landed_value(self, product: ProductModel, user_location: str = "ES") -> float:
        """
        Returns ONLY the landed value if a live offer exists (Retail or P2P).
        Used for the independent 'Landed Value' metric.
        """
        # --- LEVEL 1: RETAIL ---
        best_retail = self.db.query(OfferModel).filter(
            OfferModel.product_id == product.id,
            OfferModel.is_available == True,
            OfferModel.source_type == "Retail"
        ).order_by(OfferModel.price.asc()).first()
        
        if best_retail:
            return LogisticsService.optimized_get_landing_price(
                best_retail.price, 
                best_retail.shop_name, 
                user_location, 
                self.rules_map
            )

        # --- LEVEL 2: P2P ---
        best_p2p = self.db.query(OfferModel).filter(
            OfferModel.product_id == product.id,
            OfferModel.is_available == True,
            OfferModel.source_type == "Peer-to-Peer"
        ).order_by(OfferModel.price.asc()).first()
        
        if best_p2p:
            return LogisticsService.optimized_get_landing_price(
                best_p2p.price, 
                best_p2p.shop_name, 
                user_location, 
                self.rules_map
            )
            
        return 0.0
