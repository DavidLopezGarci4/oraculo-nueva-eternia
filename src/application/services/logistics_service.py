from datetime import datetime
from typing import Dict, Optional, List
from src.domain.models import LogisticRuleModel
from src.infrastructure.database_cloud import SessionCloud
import logging

logger = logging.getLogger(__name__)

class LogisticsService:
    """
    Oráculo Logístico (Phase 15): Servicio centralizado para el cálculo de costes de importación.
    """
    
    @staticmethod
    def get_landing_price(price: float, shop_name: str, user_location: str = "ES", item_count: int = 1) -> float:
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
            
            return LogisticsService._apply_rule(price, rule, item_count)

    @staticmethod
    def optimized_get_landing_price(price: float, shop_name: str, user_location: str, rules_map: Dict[str, LogisticRuleModel], item_count: int = 1) -> float:
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
            
        return LogisticsService._apply_rule(price, rule, item_count)

    @staticmethod
    def _apply_rule(price: float, rule: Optional[LogisticRuleModel], item_count: int = 1) -> float:
        """Aplica la lógica de la regla logística (IVA, Envío, Tasas)."""
        if not rule:
            return round(price, 2)
            
        from src.application.services.currency_service import CurrencyService
        
        # 1. Ajuste de Divisa (Phase 56)
        # BigBadToyStore y Ebay (US) usualmente vienen en USD.
        # En el futuro, el 'OfferModel' debería tener el campo currency,
        # pero por ahora lo inferimos de la tienda o regla si no viene.
        current_price = price
        if rule.shop_name == "BigBadToyStore" or rule.strategy_key == "bbts_flat_rate":
            usd_rate = CurrencyService.get_usd_to_eur_rate()
            # [3OX] El usuario quiere (Precio + Envío) * IVA.
            # Por tanto, convertimos el precio base a EUR primero.
            current_price = price * usd_rate
            logger.debug(f"Logistics: Converted ${price} to {current_price:.2f} EUR (Rate: {usd_rate})")

        base_shipping = rule.base_shipping
        
        # Estrategias especiales
        if rule.strategy_key == "tradeinn_volume":
            if item_count <= 5:
                base_shipping = 2.99
            else:
                base_shipping = 3.49
        elif rule.strategy_key == "bbts_flat_rate" or rule.strategy_key == "item_rate":
            # [3OX] El usuario pide "sumársele unos 7$ por item enviado"
            # Si es por item, multiplicamos el base_shipping por la cantidad.
            base_shipping = rule.base_shipping * item_count
            # Si el shipping está en la regla pero la regla es de BBTS (USD), 
            # también debemos convertir el envío a euros si la regla lo tiene en USD.
            # Asumimos que base_shipping en DB para BBTS está en USD.
            if rule.shop_name == "BigBadToyStore":
                usd_rate = CurrencyService.get_usd_to_eur_rate()
                base_shipping = base_shipping * usd_rate
            
        shipping_cost = base_shipping
        # El threshold de envío gratis se aplica sobre el total del carrito
        if rule.free_shipping_threshold > 0 and (current_price * item_count) >= rule.free_shipping_threshold:
            shipping_cost = 0.0
            
        # Cálculo del precio unitario de aterrizaje (Landing Price)
        # ( (PrecioUnitario_EUR * Cantidad + GastosEnvío_EUR) * MultiplicadorIVA ) + TasasEspeciales
        total_items_price = current_price * item_count
        total_taxable = total_items_price + shipping_cost
        total_landing = (total_taxable * rule.vat_multiplier) + rule.custom_fees
        
        unit_landing_price = total_landing / item_count
        
        return round(unit_landing_price, 2)

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
    @staticmethod
    def calculate_cart(items: List[dict], user_location: str = "ES") -> dict:
        """
        Calcula el desglose completo de un carrito ficticio.
        Agrupa por tienda y aplica reglas de envío por volumen/precio total.
        items: [{"shop_name": str, "price": float, "quantity": int}, ...]
        """
        from src.application.services.currency_service import CurrencyService
        
        with SessionCloud() as db:
            rules = db.query(LogisticRuleModel).all()
            rules_map = {f"{r.shop_name}_{r.country_code}": r for r in rules}
            
            # 1. Agrupar por Tienda
            shops_data = {}
            for item in items:
                shop = item["shop_name"]
                if shop not in shops_data:
                    shops_data[shop] = {"items": [], "total_qty": 0, "base_total_eur": 0.0}
                
                # Conversión de divisa si es necesario (BBTS)
                price = item["price"]
                rule_key = f"{shop}_{user_location}"
                rule = rules_map.get(rule_key) or rules_map.get(f"{shop}_ES")
                
                price_eur = price
                if rule and (rule.shop_name == "BigBadToyStore" or rule.strategy_key == "bbts_flat_rate"):
                    rate = CurrencyService.get_usd_to_eur_rate()
                    price_eur = price * rate
                
                qty = item.get("quantity", 1)
                shops_data[shop]["items"].append({
                    "name": item.get("product_name", "Desconocido"),
                    "unit_price": price,
                    "unit_price_eur": round(price_eur, 2),
                    "quantity": qty,
                    "subtotal_eur": round(price_eur * qty, 2)
                })
                shops_data[shop]["total_qty"] += qty
                shops_data[shop]["base_total_eur"] += (price_eur * qty)

            # 2. Aplicar Reglas por Tienda
            breakdown = []
            grand_total_eur = 0.0
            
            for shop, data in shops_data.items():
                rule_key = f"{shop}_{user_location}"
                rule = rules_map.get(rule_key) or rules_map.get(f"{shop}_ES")
                
                if not rule:
                    # Tienda pendiente de reglas
                    shop_total = data["base_total_eur"]
                    breakdown.append({
                        "shop": shop,
                        "status": "PENDING_RULES",
                        "items": data["items"],
                        "shipping_eur": 0.0,
                        "tax_eur": 0.0,
                        "total_eur": round(shop_total, 2)
                    })
                    grand_total_eur += shop_total
                    continue

                # Usamos la lógica unificada de _apply_rule pero adaptada al carrito (total_qty)
                # Primero calculamos el envío total para el grupo de la tienda
                base_shipping = rule.base_shipping
                item_count = data["total_qty"]
                
                if rule.strategy_key == "tradeinn_volume":
                    base_shipping = 2.99 if item_count <= 5 else 3.49
                elif rule.strategy_key == "bbts_flat_rate" or rule.strategy_key == "item_rate":
                    base_shipping = rule.base_shipping * item_count
                
                shipping_eur = base_shipping
                if rule.shop_name == "BigBadToyStore":
                    rate = CurrencyService.get_usd_to_eur_rate()
                    shipping_eur = base_shipping * rate
                
                # Envío gratis?
                if rule.free_shipping_threshold > 0 and data["base_total_eur"] >= rule.free_shipping_threshold:
                    shipping_eur = 0.0
                
                # IVA / Tasas (Basado en el total imponible de la tienda)
                total_taxable = data["base_total_eur"] + shipping_eur
                total_final = (total_taxable * rule.vat_multiplier) + rule.custom_fees
                tax_amount = (total_taxable * (rule.vat_multiplier - 1))
                
                breakdown.append({
                    "shop": shop,
                    "status": "CALCULATED",
                    "items": data["items"],
                    "total_items_qty": item_count,
                    "shipping_eur": round(shipping_eur, 2),
                    "tax_eur": round(tax_amount, 2),
                    "fees_eur": round(rule.custom_fees, 2),
                    "total_eur": round(total_final, 2)
                })
                grand_total_eur += total_final

            return {
                "breakdown": breakdown,
                "grand_total_eur": round(grand_total_eur, 2),
                "user_location": user_location,
                "timestamp": datetime.utcnow().isoformat()
            }
