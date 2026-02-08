
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

    def get_condition_multiplier(self, condition: str, grade: float = 10.0) -> float:
        """
        Calculates the value multiplier based on condition and grade.
        Standard Waterfall assumes MOC 10.
        """
        multipliers = {
            "MOC": 1.0,
            "NEW": 0.75,
            "LOOSE": 0.5
        }
        
        base_mult = multipliers.get(condition.upper(), 0.75) # Default to NEW if unknown
        
        # Grading Adjustment: -2% per 0.5 point below 10
        # Grade 9.0 = 0.96 (4% reduction)
        # Grade 8.0 = 0.92 (8% reduction)
        grade_factor = 1.0 - ((10.0 - (grade or 10.0)) * 0.04)
        grade_factor = max(0.1, grade_factor) # Never below 10%
        
        return base_mult * grade_factor

    def get_collection_valuation(self, user_id: int, user_location: str = "ES") -> dict:
        """Calculates total value of a user's collection using the waterfall and legacy context."""
        from src.domain.models import CollectionItemModel
        
        items = self.db.query(CollectionItemModel).filter(
            CollectionItemModel.owner_id == user_id,
            CollectionItemModel.acquired == True
        ).all()
        
        total_value = 0.0
        total_invested = 0.0
        total_landed_market = 0.0 
        
        for item in items:
            # 1. Base Market Value (The Oracle)
            base_market_value = self.get_consolidated_value(item.product, user_location)
            
            # 2. Apply Personal Legado Multipliers (Condition & Grade)
            multiplier = self.get_condition_multiplier(item.condition, item.grading)
            adjusted_value = base_market_value * multiplier
            
            total_value += adjusted_value
            total_invested += (item.purchase_price or 0.0)
            
            # 3. Real Landed Value (Market Context)
            landed = self.get_pure_landed_value(item.product, user_location)
            total_landed_market += (landed * multiplier if landed else adjusted_value)
            
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
