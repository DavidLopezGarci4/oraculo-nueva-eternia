from typing import Optional
from src.domain.models import ProductModel
import logging

logger = logging.getLogger(__name__)

class DealScorer:
    """
    Servicio de Inteligencia Financiera (Phase 18).
    Calcula el 'Opportunity Score' (1-100) basandose en MSRP, P25 y Wishlist.
    """

    @staticmethod
    def calculate_score(product: ProductModel, landed_price: float, is_wish: bool = False) -> int:
        """
        Calcula la puntuación de oportunidad del 1 al 100.
        """
        if landed_price <= 0:
            return 0
            
        score = 0
        
        # 1. Vector Retail (MSRP) - Max 40 pts
        # Premia el ahorro respecto al precio de lanzamiento oficial.
        msrp = product.retail_price or 0.0
        if msrp > 0:
            retail_savings_pct = (msrp - landed_price) / msrp
            # 30% de ahorro o más otorga los 40 puntos máximos
            retail_pts = min(40, max(0, int((retail_savings_pct / 0.30) * 40)))
            score += retail_pts

        # 2. Vector Mercado (P25 Floor) - Max 40 pts
        # Premia la ventaja respecto al suelo de mercado de segunda mano.
        p25 = product.p25_price or 0.0
        if p25 > 0:
            market_advantage_pct = (p25 - landed_price) / p25
            # Precio igual a P25 = 20 pts. 
            # Precio 10% inferior a P25 o más = 40 pts.
            if landed_price <= p25:
                # Partimos de 20 pts por estar en suelo.
                # Ganamos 20 pts extra si llegamos al 10% de ventaja.
                bonus_pts = min(20, max(0, int((market_advantage_pct / 0.10) * 20)))
                score += (20 + bonus_pts)
            else:
                # Si es más caro que P25, pts decrecientes (0 si es 20% más caro que P25)
                over_p25_pct = (landed_price - p25) / p25
                market_pts = max(0, int(20 - (over_p25_pct / 0.20) * 20))
                score += market_pts

        # 3. Vector Deseo (Wishlist) - Max 20 pts
        if is_wish:
            score += 20
            
        return min(100, score)

    @staticmethod
    def is_mandatory_buy(product: ProductModel, landed_price: float, score: int) -> bool:
        """
        Determina si una oferta cumple los criterios de 'Compra Obligatoria'.
        """
        msrp = product.retail_price or 0.0
        if msrp <= 0:
            return False
            
        # Criterio: Score >= 90 Y Ahorro Real > 20% sobre MSRP
        has_high_score = score >= 90
        has_significant_saving = landed_price <= (0.80 * msrp)
        
        return has_high_score and has_significant_saving
