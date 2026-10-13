from typing import Dict, Any, List, Optional
from loguru import logger

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel, OfferModel, PendingMatchModel, LogisticRuleModel, CollectionItemModel
from src.application.services.logistics_service import LogisticsService

class BudgetOptimizerService:
    """
    Asistente de Presupuesto y Carrito Multi-Tienda (Matrix Cart).
    Encuentra la combinación óptima de compras dentro de un presupuesto dado,
    amortizando gastos de envío y maximizando el ahorro de la colección.
    """

    @classmethod
    def optimize_cart(
        cls,
        budget_limit: float,
        user_id: int = 2,
        target_product_ids: Optional[List[int]] = None,
        user_location: str = "ES"
    ) -> Dict[str, Any]:
        with SessionCloud() as db:
            # 1. Precargar reglas logísticas
            rules = db.query(LogisticRuleModel).all()
            rules_map = {f"{r.shop_name}_{r.country_code}": r for r in rules}

            # 2. Obtener productos objetivo (Wishlist o productos no poseídos)
            if target_product_ids:
                products = db.query(ProductModel).filter(
                    ProductModel.id.in_(target_product_ids),
                    ProductModel.is_vintage == False
                ).all()
            else:
                owned_ids = {
                    i.product_id for i in db.query(CollectionItemModel.product_id).filter(
                        CollectionItemModel.owner_id == user_id,
                        CollectionItemModel.acquired == True
                    ).all()
                }
                products = db.query(ProductModel).filter(
                    ProductModel.id.notin_(owned_ids),
                    ProductModel.is_vintage == False
                ).all()

            product_map = {p.id: p for p in products}
            if not product_map:
                return {
                    "budget_limit": budget_limit,
                    "total_spent": 0.0,
                    "remaining_budget": budget_limit,
                    "savings_total": 0.0,
                    "items_count": 0,
                    "selected_items": [],
                    "stores_breakdown": {}
                }

            # 3. Recolectar todas las ofertas válidas para estos productos
            candidates = []
            
            # A) Ofertas de tiendas
            offers = db.query(OfferModel).filter(
                OfferModel.product_id.in_(list(product_map.keys())),
                OfferModel.is_available == True,
                OfferModel.price > 0
            ).all()

            for o in offers:
                p = product_map[o.product_id]
                benchmark = p.p25_price or p.retail_price or 19.99
                landed = LogisticsService.optimized_get_landing_price(
                    price=o.price,
                    shop_name=o.shop_name,
                    user_location=user_location,
                    rules_map=rules_map,
                    item_count=1
                )
                savings = max(0.0, benchmark - landed)
                candidates.append({
                    "product_id": p.id,
                    "product_name": p.name,
                    "base_price": o.price,
                    "landed_price": landed,
                    "benchmark_price": benchmark,
                    "savings_amount": savings,
                    "savings_pct": round((savings / benchmark * 100), 1) if benchmark > 0 else 0,
                    "shop_name": o.shop_name,
                    "url": o.url,
                    "image_url": o.image_url or p.image_url
                })

            # B) Ofertas del Purgatorio vinculables
            matches = db.query(PendingMatchModel).filter(
                PendingMatchModel.validation_status == "PENDING",
                PendingMatchModel.is_blocked == False,
                PendingMatchModel.price > 0
            ).all()

            for m in matches:
                # Buscar si coincide con alguno de nuestros productos objetivo
                for p_id, p in product_map.items():
                    if p.name.lower() in m.scraped_name.lower():
                        benchmark = p.p25_price or p.retail_price or 19.99
                        landed = LogisticsService.optimized_get_landing_price(
                            price=m.price,
                            shop_name=m.shop_name,
                            user_location=user_location,
                            rules_map=rules_map,
                            item_count=1
                        )
                        savings = max(0.0, benchmark - landed)
                        candidates.append({
                            "product_id": p.id,
                            "product_name": p.name,
                            "base_price": m.price,
                            "landed_price": landed,
                            "benchmark_price": benchmark,
                            "savings_amount": savings,
                            "savings_pct": round((savings / benchmark * 100), 1) if benchmark > 0 else 0,
                            "shop_name": m.shop_name,
                            "url": m.url,
                            "image_url": m.image_url or p.image_url
                        })
                        break

            # 4. Ordenar candidatos por mejor relación de ahorro por euro gastado (Deal Density)
            candidates.sort(
                key=lambda x: (x["savings_amount"] / max(1.0, x["landed_price"]), -x["landed_price"]),
                reverse=True
            )

            # 5. Algoritmo Voraz con Agrupación Logística Multi-Tienda (Amortización de Envío y Umbral Envío Gratis)
            def _compute_shop_bundle_landed(shop_name: str, shop_items: List[Dict[str, Any]]) -> float:
                if not shop_items:
                    return 0.0
                count = len(shop_items)
                avg_base = sum(float(i["base_price"]) for i in shop_items) / count
                unit_landed = LogisticsService.optimized_get_landing_price(
                    price=avg_base,
                    shop_name=shop_name,
                    user_location=user_location,
                    rules_map=rules_map,
                    item_count=count,
                )
                return round(unit_landed * count, 2)

            selected_items = []
            selected_by_shop: Dict[str, List[Dict[str, Any]]] = {}
            seen_products = set()
            current_total = 0.0

            for c in candidates:
                if c["product_id"] in seen_products:
                    continue
                shop = c["shop_name"]
                existing_shop_items = selected_by_shop.get(shop, [])
                old_shop_landed = _compute_shop_bundle_landed(shop, existing_shop_items)
                new_shop_landed = _compute_shop_bundle_landed(shop, existing_shop_items + [c])
                marginal_cost = round(new_shop_landed - old_shop_landed, 2)

                if round(current_total + marginal_cost, 2) <= budget_limit:
                    selected_items.append(c)
                    selected_by_shop.setdefault(shop, []).append(c)
                    seen_products.add(c["product_id"])
                    current_total = round(current_total + marginal_cost, 2)

            # 6. Agrupar desglose por tienda y cuantificar envío ahorrado por agrupación
            stores_breakdown = {}
            total_item_savings = 0.0
            total_shipping_saved = 0.0

            for shop, items in selected_by_shop.items():
                total_base = round(sum(float(i["base_price"]) for i in items), 2)
                unbundled_landed = round(sum(float(i["landed_price"]) for i in items), 2)
                bundled_landed = _compute_shop_bundle_landed(shop, items)
                shipping_saved = round(max(0.0, unbundled_landed - bundled_landed), 2)
                total_shipping_saved += shipping_saved
                total_item_savings += sum(float(i["savings_amount"]) for i in items)

                stores_breakdown[shop] = {
                    "shop_name": shop,
                    "items_count": len(items),
                    "total_base": total_base,
                    "total_landed": bundled_landed,
                    "unbundled_landed": unbundled_landed,
                    "shipping_saved": shipping_saved,
                    "items": items,
                }

            return {
                "budget_limit": budget_limit,
                "total_spent": round(current_total, 2),
                "remaining_budget": round(budget_limit - current_total, 2),
                "savings_total": round(total_item_savings + total_shipping_saved, 2),
                "shipping_saved": round(total_shipping_saved, 2),
                "items_count": len(selected_items),
                "selected_items": selected_items,
                "stores_breakdown": stores_breakdown
            }
