from typing import Dict, Optional
from src.domain.models import LogisticRuleModel
from src.infrastructure.database_cloud import SessionCloud
import logging

logger = logging.getLogger(__name__)

class LogisticsService:
    """
    Oráculo Logístico (Phase 15): Servicio centralizado para el cálculo de costes de importación.
    """
    
    @staticmethod
    def get_landing_price(price: float, shop_name: str, user_location: str = "ES") -> float:
        """
        Calcula el 'Precio de Aterrizaje' sumando IVA/Tasas y Gastos de Envío.
        Versión Estándar (Consulta DB individual).
        """
        with SessionCloud() as db:
            rule = db.query(LogisticRuleModel).filter(
                LogisticRuleModel.shop_name == shop_name,
                LogisticRuleModel.country_code == user_location
            ).first()
            
            if not rule:
                rule = db.query(LogisticRuleModel).filter(
                    LogisticRuleModel.shop_name == shop_name,
                    LogisticRuleModel.country_code == "ES"
                ).first()
            
            return LogisticsService._apply_rule(price, rule)

    @staticmethod
    def optimized_get_landing_price(price: float, shop_name: str, user_location: str, rules_map: Dict[str, LogisticRuleModel]) -> float:
        """
        Versión de ALTO RENDIMIENTO (Phase 18 Optimization).
        Recibe un mapa de reglas pre-cargadas para evitar miles de consultas a la DB.
        """
        # Intentar regla específica
        key = f"{shop_name}_{user_location}"
        rule = rules_map.get(key)
        
        # Fallback a regla ES
        if not rule:
            key_es = f"{shop_name}_ES"
            rule = rules_map.get(key_es)
            
        return LogisticsService._apply_rule(price, rule)

    @staticmethod
    def _apply_rule(price: float, rule: Optional[LogisticRuleModel]) -> float:
        """Aplica la lógica de la regla logística (IVA, Envío, Tasas)."""
        if not rule:
            return round(price, 2)
            
        base_shipping = rule.base_shipping
        
        # Estrategias especiales
        if rule.strategy_key == "bbts_flat_rate":
            base_shipping = rule.base_shipping
            
        shipping_cost = base_shipping
        if rule.free_shipping_threshold > 0 and price >= rule.free_shipping_threshold:
            shipping_cost = 0.0
            
        total_taxable = price + shipping_cost
        landing_price = (total_taxable * rule.vat_multiplier) + rule.custom_fees
        
        return round(landing_price, 2)

    @staticmethod
    def calculate_roi(market_value: float, landing_price: float) -> float:
        """
        Calcula el Retorno de Inversión basado en el Precio de Aterrizaje.
        """
        if landing_price <= 0:
            return 0.0
        
        roi_val = ((market_value - landing_price) / landing_price) * 100
        return round(roi_val, 1)

    @staticmethod
    def get_rules_by_shop(shop_name: str) -> Dict[str, LogisticRuleModel]:
        """Retorna todas las reglas geográficas para una tienda específica."""
        with SessionCloud() as db:
            rules = db.query(LogisticRuleModel).filter(LogisticRuleModel.shop_name == shop_name).all()
            return {r.country_code: r for r in rules}
