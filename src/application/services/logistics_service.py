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
        Nueva Fórmula: (Precio + Envío) * VAT_Multiplier + Custom_Fees
        """
        with SessionCloud() as db:
            # Buscar regla específica para la tienda y ubicación
            rule = db.query(LogisticRuleModel).filter(
                LogisticRuleModel.shop_name == shop_name,
                LogisticRuleModel.country_code == user_location
            ).first()
            
            if not rule:
                # Si no hay regla, intentamos buscar la regla por defecto para la tienda (ubicación ES)
                rule = db.query(LogisticRuleModel).filter(
                    LogisticRuleModel.shop_name == shop_name,
                    LogisticRuleModel.country_code == "ES"
                ).first()
            
            if not rule:
                return round(price, 2)
            
            # 1. Determinar el coste de envío base (posible lógica por estrategia)
            base_shipping = rule.base_shipping
            
            # Estrategia BBTS: Si el item es pequeño/ligero (asumido por ahora), aplicar tarifa plana
            if rule.strategy_key == "bbts_flat_rate":
                # Si en el futuro tenemos peso en OfferModel, podríamos ajustarlo aquí
                base_shipping = rule.base_shipping # Ya configurado como 7.50€ ($8) en seed
                
            # 2. Verificar umbral de envío gratuito (solo si no es exportación internacional)
            # Nota: Normalmente el envío gratis solo aplica en local.
            shipping_cost = base_shipping
            if rule.free_shipping_threshold > 0 and price >= rule.free_shipping_threshold:
                shipping_cost = 0.0
                
            # 3. Aplicar Fórmula Maestra
            # El IVA se aplica sobre (Precio + Envío) en importaciones
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
