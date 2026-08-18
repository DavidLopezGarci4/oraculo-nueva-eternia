from datetime import datetime, timezone
from typing import Dict, Optional, List
from src.domain.models import LogisticRuleModel
from src.infrastructure.database_cloud import SessionCloud
import logging

logger = logging.getLogger(__name__)

SHOP_ALIASES = {
    "toymi": "ToymiEU",
    "toymieu": "ToymiEU",
    "fantasia": "Fantasia Personajes",
    "fantasia personajes": "Fantasia Personajes",
    "tradeinn": "Tradeinn",
    "tradeinn (kidinn)": "Tradeinn",
    "tradeinn (techinn)": "Tradeinn",
    "tradeinn (dressinn)": "Tradeinn",
    "kidinn": "Tradeinn",
    "techinn": "Tradeinn",
    "wallapop": "Wallapop",
    "wallapopmanual": "Wallapop",
    "ebay": "Ebay.es",
    "ebay.es": "Ebay.es",
    "ebay.com": "Ebay.es",
    "ebay es": "Ebay.es",
    "frikimaz": "Frikimaz",
    "triguetech": "Triguetech",
    "lamansiondelterror": "LaMansionDelTerror",
    "la mansion del terror": "LaMansionDelTerror",
    "vinted": "Vinted",
}

DEFAULT_FALLBACK_RULE = LogisticRuleModel(
    shop_name="Standard",
    country_code="ES",
    base_shipping=4.95,
    free_shipping_threshold=80.0,
    vat_multiplier=1.0,
    custom_fees=0.0,
    strategy_key=None,
)


class LogisticsService:
    """
    Oráculo Logístico (Phase 15/18/42): Servicio centralizado para el cálculo de costes de importación,
    tarifas comerciales, seguros P2P y precio final puesto en casa (Landed Price).
    """

    @staticmethod
    def normalize_shop_name(shop_name: str) -> str:
        """Normaliza el nombre de la tienda para resolver alias conocidos."""
        if not shop_name:
            return ""
        clean = shop_name.strip()
        return SHOP_ALIASES.get(clean.lower(), clean)

    @staticmethod
    def _resolve_rule(
        shop_name: str,
        user_location: str,
        rules_map: Dict[str, LogisticRuleModel]
    ) -> Optional[LogisticRuleModel]:
        """Resuelve la regla logística para una tienda y ubicación con fallback inteligente."""
        canonical = LogisticsService.normalize_shop_name(shop_name)
        
        # 1. Búsqueda exacta
        rule = rules_map.get(f"{canonical}_{user_location}")
        if rule:
            return rule

        # 2. Fallback a España (ES)
        rule = rules_map.get(f"{canonical}_ES")
        if rule:
            return rule

        # 3. Fallback por nombre original si difiere
        if canonical != shop_name:
            rule = rules_map.get(f"{shop_name}_{user_location}") or rules_map.get(f"{shop_name}_ES")
            if rule:
                return rule

        return None

    @staticmethod
    def get_landing_price(price: float, shop_name: str, user_location: str = "ES", item_count: int = 1) -> float:
        """
        Calcula el 'Precio de Aterrizaje' sumando IVA/Tasas y Gastos de Envío.
        Versión Estándar (Consulta DB individual).
        """
        with SessionCloud() as db:
            rules = db.query(LogisticRuleModel).all()
            rules_map = {f"{r.shop_name}_{r.country_code}": r for r in rules}
            return LogisticsService.optimized_get_landing_price(price, shop_name, user_location, rules_map, item_count)

    @staticmethod
    def optimized_get_landing_price(
        price: float,
        shop_name: str,
        user_location: str,
        rules_map: Dict[str, LogisticRuleModel],
        item_count: int = 1
    ) -> float:
        """
        Versión de ALTO RENDIMIENTO (Phase 18 Optimization).
        Recibe un mapa de reglas pre-cargadas para evitar consultas repetitivas a la DB.
        """
        rule = LogisticsService._resolve_rule(shop_name, user_location, rules_map)
        return LogisticsService._apply_rule(price, rule, item_count)

    @staticmethod
    def _apply_rule(price: float, rule: Optional[LogisticRuleModel], item_count: int = 1) -> float:
        """Aplica la lógica de la regla logística (IVA, Envío, Tasas, Seguros P2P)."""
        if price <= 0:
            return 0.0
        if not rule:
            return round(price, 2)
            
        from src.application.services.currency_service import CurrencyService

        item_count = max(1, item_count)
        current_price = price
        base_shipping = rule.base_shipping
        strategy = rule.strategy_key

        # 1. BigBadToyStore: USD -> EUR + 8$ envío por ítem + 21% IVA sobre total
        if rule.shop_name == "BigBadToyStore" or strategy == "bbts_flat_rate":
            usd_rate = CurrencyService.get_usd_to_eur_rate()
            # 8$ de envío por ítem
            shipping_usd = 8.00 * item_count
            total_items_usd = price * item_count
            total_taxable_usd = total_items_usd + shipping_usd
            total_taxable_eur = total_taxable_usd * usd_rate
            total_landing = total_taxable_eur * 1.21 + rule.custom_fees
            return round(total_landing / item_count, 2)

        # 2. P2P Marketplaces (Ebay.es, Wallapop, Vinted): Envío 5€ + 2% Seguro sobre ítem
        if strategy == "p2p_insurance" or rule.shop_name in ("Ebay.es", "Wallapop", "Vinted"):
            total_items = current_price * item_count
            insurance_fee = total_items * 0.02 # 2% de protección
            shipping_cost = 5.00
            total_landing = total_items + insurance_fee + shipping_cost + rule.custom_fees
            return round(total_landing / item_count, 2)

        # 3. Triguetech: Tarifa plana fija de 7€ independientemente de los ítems
        if strategy == "triguetech_flat_rate" or rule.shop_name == "Triguetech":
            total_items = current_price * item_count
            shipping_cost = 7.00
            total_landing = (total_items + shipping_cost) * rule.vat_multiplier + rule.custom_fees
            return round(total_landing / item_count, 2)

        # 4. Tiendas estándar con posible umbral de envío gratis
        total_items_price = current_price * item_count
        shipping_cost = base_shipping

        # Umbral de envío gratis
        if rule.free_shipping_threshold > 0 and total_items_price >= rule.free_shipping_threshold:
            shipping_cost = 0.0

        total_taxable = total_items_price + shipping_cost
        total_landing = (total_taxable * rule.vat_multiplier) + rule.custom_fees
        
        return round(total_landing / item_count, 2)

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
        canonical = LogisticsService.normalize_shop_name(shop_name)
        with SessionCloud() as db:
            rules = db.query(LogisticRuleModel).filter(
                (LogisticRuleModel.shop_name == canonical) | (LogisticRuleModel.shop_name == shop_name)
            ).all()
            return {r.country_code: r for r in rules}

    @staticmethod
    def calculate_cart(items: List[dict], user_location: str = "ES") -> dict:
        """
        Calcula el desglose completo de un carrito ficticio.
        Agrupa por tienda y aplica reglas de envío por volumen/precio total y seguros.
        items: [{"shop_name": str, "price": float, "quantity": int}, ...]
        """
        from src.application.services.currency_service import CurrencyService
        
        with SessionCloud() as db:
            rules = db.query(LogisticRuleModel).all()
            rules_map = {f"{r.shop_name}_{r.country_code}": r for r in rules}
            
            # 1. Agrupar por Tienda Canónica
            shops_data = {}
            for item in items:
                raw_shop = item.get("shop_name", "Desconocido")
                canonical_shop = LogisticsService.normalize_shop_name(raw_shop)
                
                if canonical_shop not in shops_data:
                    shops_data[canonical_shop] = {
                        "display_name": canonical_shop,
                        "items": [],
                        "total_qty": 0,
                        "base_total_eur": 0.0,
                        "rule": LogisticsService._resolve_rule(canonical_shop, user_location, rules_map)
                    }
                
                rule = shops_data[canonical_shop]["rule"]
                price = float(item.get("price", 0.0))
                price_eur = price

                # Conversión USD para BBTS
                if rule and (rule.shop_name == "BigBadToyStore" or rule.strategy_key == "bbts_flat_rate"):
                    rate = CurrencyService.get_usd_to_eur_rate()
                    price_eur = price * rate
                
                qty = int(item.get("quantity", 1))
                shops_data[canonical_shop]["items"].append({
                    "name": item.get("product_name", "Desconocido"),
                    "unit_price": price,
                    "unit_price_eur": round(price_eur, 2),
                    "quantity": qty,
                    "subtotal_eur": round(price_eur * qty, 2)
                })
                shops_data[canonical_shop]["total_qty"] += qty
                shops_data[canonical_shop]["base_total_eur"] += (price_eur * qty)

            # 2. Aplicar Reglas por Tienda
            breakdown = []
            grand_total_eur = 0.0
            
            for shop_name, data in shops_data.items():
                rule = data["rule"]
                item_count = data["total_qty"]
                base_total = data["base_total_eur"]

                if not rule:
                    # Tienda sin regla en DB -> PENDING_RULES
                    shop_total = base_total
                    breakdown.append({
                        "shop": shop_name,
                        "status": "PENDING_RULES",
                        "items": data["items"],
                        "shipping_eur": 0.0,
                        "tax_eur": 0.0,
                        "total_eur": round(shop_total, 2)
                    })
                    grand_total_eur += shop_total
                    continue

                strategy = rule.strategy_key

                # Caso A: BigBadToyStore (USD $8/item + 21% IVA)
                if rule.shop_name == "BigBadToyStore" or strategy == "bbts_flat_rate":
                    rate = CurrencyService.get_usd_to_eur_rate()
                    shipping_usd = 8.00 * item_count
                    shipping_eur = shipping_usd * rate
                    total_taxable = base_total + shipping_eur
                    tax_amount = total_taxable * 0.21 # 21% IVA
                    total_final = total_taxable + tax_amount + rule.custom_fees

                # Caso B: P2P Marketplaces (Ebay.es, Wallapop, Vinted): Envío 5€ + 2% Seguro
                elif strategy == "p2p_insurance" or rule.shop_name in ("Ebay.es", "Wallapop", "Vinted"):
                    shipping_eur = 5.00
                    tax_amount = base_total * 0.02 # Seguro de protección 2%
                    total_final = base_total + shipping_eur + tax_amount + rule.custom_fees

                # Caso C: Triguetech (7.00€ tarifa plana fija por pedido)
                elif strategy == "triguetech_flat_rate" or rule.shop_name == "Triguetech":
                    shipping_eur = 7.00
                    tax_amount = 0.0
                    total_final = base_total + shipping_eur + rule.custom_fees

                # Caso D: Tiendas estándar (Frikimaz > 69€ gratis, etc.)
                else:
                    shipping_eur = rule.base_shipping
                    if rule.free_shipping_threshold > 0 and base_total >= rule.free_shipping_threshold:
                        shipping_eur = 0.0
                    
                    total_taxable = base_total + shipping_eur
                    total_final = (total_taxable * rule.vat_multiplier) + rule.custom_fees
                    tax_amount = total_taxable * (rule.vat_multiplier - 1)

                breakdown.append({
                    "shop": shop_name,
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
                "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
            }
