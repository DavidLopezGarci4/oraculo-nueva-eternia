from sqlalchemy.orm import Session, contains_eager
from src.domain.models import OfferModel, ProductModel, LogisticRuleModel
from src.application.services.logistics_service import LogisticsService
import logging

logger = logging.getLogger("ValuationService")


class ValuationService:
    def __init__(self, db: Session):
        self.db = db
        # Use process-level cached logistics rules (10-minute TTL)
        self.rules_map = LogisticsService.get_cached_rules_map(self.db)
        self.preloaded_offers: dict[int, list[OfferModel]] = {}

    def preload_offers_for_products(self, product_ids: list[int]):
        """Pre-carga ofertas activas para optimizar consultas N+1 en loops."""
        if not product_ids:
            self.preloaded_offers = {}
            return

        # Inicializar listas vacías para todos los product_ids solicitados
        # evitando que productos con 0 ofertas disparen queries N+1 de fallback.
        self.preloaded_offers = {pid: [] for pid in product_ids if pid is not None}

        offers = (
            self.db.query(OfferModel)
            .filter(
                OfferModel.product_id.in_(list(self.preloaded_offers.keys())),
                OfferModel.is_available == True,
            )
            .all()
        )

        for o in offers:
            self.preloaded_offers.setdefault(o.product_id, []).append(o)

    def _compute_best_landed_by_channel(
        self, product: ProductModel, user_location: str = "ES"
    ) -> tuple[float | None, float | None]:
        """Single pass over a product's active offers returning (best_retail_landed, best_p2p_landed)."""
        best_retail_landed = None
        best_p2p_landed = None

        product_offers = self.preloaded_offers.get(product.id)
        if product_offers is None:
            product_offers = (
                self.db.query(OfferModel)
                .filter(
                    OfferModel.product_id == product.id,
                    OfferModel.is_available == True,
                )
                .all()
            )
            self.preloaded_offers[product.id] = product_offers

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

        return best_retail_landed, best_p2p_landed

    def get_product_valuation_pair(
        self, product: ProductModel, user_location: str = "ES"
    ) -> tuple[float, float]:
        """
        Single-pass computation returning (consolidated_value, pure_landed_value).
        Avoids scanning offers twice per collection item.
        """
        best_retail_landed, best_p2p_landed = self._compute_best_landed_by_channel(
            product, user_location
        )

        if best_retail_landed is not None:
            pure_landed = best_retail_landed
        elif best_p2p_landed is not None:
            pure_landed = best_p2p_landed
        else:
            pure_landed = 0.0

        if pure_landed > 0:
            consolidated = pure_landed
        elif product.avg_market_price and product.avg_market_price > 0:
            consolidated = product.avg_market_price
        elif product.avg_p2p_price and product.avg_p2p_price > 0:
            consolidated = product.avg_p2p_price
        elif product.avg_retail_price and product.avg_retail_price > 0:
            consolidated = product.avg_retail_price
        elif product.retail_price and product.retail_price > 0:
            consolidated = product.retail_price
        else:
            consolidated = 0.0

        return consolidated, pure_landed

    def get_consolidated_value(self, product: ProductModel, user_location: str = "ES") -> float:
        """
        Implementation of the VALUATION WATERFALL.
        Returns the best possible market value estimation.
        """
        consolidated, _ = self.get_product_valuation_pair(product, user_location)
        return consolidated

    def get_condition_multiplier(self, condition: str, grade: float = 10.0) -> float:
        """
        Calculates the value multiplier based on condition and grade.
        Standard Waterfall assumes MOC 10.
        """
        multipliers = {
            "MOC": 1.0,
            "NEW": 0.75,
            "LOOSE": 0.5,
        }

        base_mult = multipliers.get((condition or "MOC").upper(), 1.0)

        # Grading Adjustment: -2% per 0.5 point below 10
        grade_factor = 1.0 - ((10.0 - (grade or 10.0)) * 0.04)
        grade_factor = max(0.1, grade_factor)

        return base_mult * grade_factor

    def get_collection_valuation(
        self, user_id: int, user_location: str = "ES", is_vintage: bool = None
    ) -> dict:
        """Calculates total value of a user's collection using the waterfall and legacy context."""
        from src.domain.models import CollectionItemModel

        query = (
            self.db.query(CollectionItemModel)
            .join(ProductModel)
            .options(contains_eager(CollectionItemModel.product))
            .filter(
                CollectionItemModel.owner_id == user_id,
                CollectionItemModel.acquired == True,
            )
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
            if not item.product:
                continue
            # Single-pass computation of consolidated and pure landed values
            base_market_value, landed = self.get_product_valuation_pair(
                item.product, user_location
            )

            multiplier = self.get_condition_multiplier(item.condition, item.grading)
            adjusted_value = base_market_value * multiplier

            total_value += adjusted_value
            total_invested += item.purchase_price or 0.0
            total_landed_market += landed * multiplier if landed else adjusted_value

        profit_loss = total_value - total_invested
        roi = (profit_loss / total_invested * 100) if total_invested > 0 else 0.0

        return {
            "total_value": round(total_value, 2),
            "total_invested": round(total_invested, 2),
            "landed_market_value": round(total_landed_market, 2),
            "profit_loss": round(profit_loss, 2),
            "roi": round(roi, 1),
            "item_count": len(items),
        }

    def get_pure_landed_value(self, product: ProductModel, user_location: str = "ES") -> float:
        """
        Returns ONLY the landed value if a live offer exists (Retail or P2P).
        Used for the independent 'Landed Value' metric.
        """
        _, pure_landed = self.get_product_valuation_pair(product, user_location)
        return pure_landed
