
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
        self.preloaded_offers = {}

    def preload_offers_for_products(self, product_ids: list[int]):
        """Pre-carga ofertas activas para optimizar consultas N+1 en loops."""
        if not product_ids:
            return
        
        offers = self.db.query(OfferModel).filter(
            OfferModel.product_id.in_(product_ids),
            OfferModel.is_available == True
        ).all()
        
        self.preloaded_offers = {}
        for o in offers:
            self.preloaded_offers.setdefault(o.product_id, []).append(o)

    def get_consolidated_value(self, product: ProductModel, user_location: str = "ES") -> float:
        """
        Implementation of the VALUATION WATERFALL.
        Returns the best possible market value estimation.
        """
        best_retail_landed = None
        best_p2p_landed = None
        
        product_offers = self.preloaded_offers.get(product.id)
        if product_offers is None:
            product_offers = self.db.query(OfferModel).filter(
                OfferModel.product_id == product.id,
                OfferModel.is_available == True
            ).all()

        for o in product_offers:
            if not o.price or o.price <= 0:
                continue
            landed = LogisticsService.optimized_get_landing_price(
                o.price, o.shop_name, user_location, self.rules_map
            )
            if o.source_type == "Retail":
                if best_retail_landed is None or landed < best_retail_landed:
                    best_retail_landed = landed
            elif o.source_type == "Peer-to-Peer":
                if best_p2p_landed is None or landed < best_p2p_landed:
                    best_p2p_landed = landed
        
        # --- LEVEL 1: ACTIVE RETAIL OFFER (BEST LANDED) ---
        if best_retail_landed is not None:
            return best_retail_landed

        # --- LEVEL 2: ACTIVE P2P OFFER (BEST LANDED) ---
        if best_p2p_landed is not None:
            return best_p2p_landed

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
        
        base_mult = multipliers.get(condition.upper(), 1.0) # Default to MOC if unknown
        
        # Grading Adjustment: -2% per 0.5 point below 10
        # Grade 9.0 = 0.96 (4% reduction)
        # Grade 8.0 = 0.92 (8% reduction)
        grade_factor = 1.0 - ((10.0 - (grade or 10.0)) * 0.04)
        grade_factor = max(0.1, grade_factor) # Never below 10%
        
        return base_mult * grade_factor

    def get_collection_valuation(self, user_id: int, user_location: str = "ES", is_vintage: bool = None) -> dict:
        """Calculates total value of a user's collection using the waterfall and legacy context."""
        from src.domain.models import CollectionItemModel
        
        query = self.db.query(CollectionItemModel).join(ProductModel).filter(
            CollectionItemModel.owner_id == user_id,
            CollectionItemModel.acquired == True
        )
        if is_vintage is not None:
            if is_vintage:
                query = query.filter(ProductModel.is_vintage == True)
            else:
                query = query.filter(ProductModel.is_vintage.is_not(True))
                
        items = query.all()

        # Pre-cargar ofertas activas para optimizar consultas N+1 en loops
        product_ids = [item.product_id for item in items if item.product_id]
        self.preload_offers_for_products(product_ids)
        
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
        best_retail_landed = None
        best_p2p_landed = None
        
        product_offers = self.preloaded_offers.get(product.id)
        if product_offers is None:
            product_offers = self.db.query(OfferModel).filter(
                OfferModel.product_id == product.id,
                OfferModel.is_available == True
            ).all()

        for o in product_offers:
            if not o.price or o.price <= 0:
                continue
            landed = LogisticsService.optimized_get_landing_price(
                o.price, o.shop_name, user_location, self.rules_map
            )
            if o.source_type == "Retail":
                if best_retail_landed is None or landed < best_retail_landed:
                    best_retail_landed = landed
            elif o.source_type == "Peer-to-Peer":
                if best_p2p_landed is None or landed < best_p2p_landed:
                    best_p2p_landed = landed
            
        # --- LEVEL 1: RETAIL ---
        if best_retail_landed is not None:
            return best_retail_landed

        # --- LEVEL 2: P2P ---
        if best_p2p_landed is not None:
            return best_p2p_landed
            
        return 0.0

