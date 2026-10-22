# Services: LogisticsService, LogisticRuleModel

> 62 nodes

## Key Concepts

- **LogisticsService** (62 connections) — `src/application/services/logistics_service.py`
- **LogisticRuleModel** (36 connections) — `src/domain/models.py`
- **.get_landing_price()** (21 connections) — `src/application/services/logistics_service.py`
- **test_logistics_and_pricing.py** (18 connections) — `tests/integration/test_logistics_and_pricing.py`
- **BudgetOptimizerService** (16 connections) — `src/application/services/budget_optimizer_service.py`
- **unit/test_market_analytics.py** (16 connections) — `tests/unit/test_market_analytics.py`
- **.optimized_get_landing_price()** (15 connections) — `src/application/services/logistics_service.py`
- **budget_optimizer_service.py** (15 connections) — `src/application/services/budget_optimizer_service.py`
- **CurrencyService** (9 connections) — `src/application/services/currency_service.py`
- **get_top_deals()** (9 connections) — `src/interfaces/api/routers/dashboard.py`
- **test_budget_optimizer.py** (9 connections) — `tests/unit/test_budget_optimizer.py`
- **recover_and_normalize()** (8 connections) — `scripts/restore_intelligence.py`
- **.optimize_cart()** (8 connections) — `src/application/services/budget_optimizer_service.py`
- **.calculate_cart()** (8 connections) — `src/application/services/logistics_service.py`
- **get_product_offers()** (8 connections) — `src/interfaces/api/routers/products.py`
- **check_scoring()** (7 connections) — `scripts/diagnostics/check_scoring.py`
- **repair_scores()** (7 connections) — `scripts/maintenance/repair_opportunity_scores.py`
- **recover_and_normalize()** (7 connections) — `scripts/restore_cloud.py`
- **test_budget_optimizer_greedy_selection()** (7 connections) — `tests/unit/test_budget_optimizer.py`
- **verify_logistics.py** (7 connections) — `scripts/verify_logistics.py`
- **.normalize_shop_name()** (6 connections) — `src/application/services/logistics_service.py`
- **._resolve_rule()** (6 connections) — `src/application/services/logistics_service.py`
- **test_budget_optimizer_bundles_same_store_shipping()** (6 connections) — `tests/unit/test_market_analytics.py`
- **test_retail_scarcity_alerts_detects_single_retail_store()** (6 connections) — `tests/unit/test_market_analytics.py`
- **test_logistics_scenarios.py** (6 connections) — `scripts/test_logistics_scenarios.py`
- *... and 37 more nodes in this community*

## Relationships

- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (35 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (31 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (17 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (17 shared connections)
- [Routers: MarketAnalyticsService, analytics.py](Routers-_MarketAnalyticsService,_analytics.py.md) (13 shared connections)
- [Services: dashboard.py, ValuationService](Services-_dashboard.py,_ValuationService.md) (8 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (7 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (6 shared connections)
- [Tests: conftest.py, unittest_mock](Tests-_conftest.py,_unittest_mock.md) (4 shared connections)
- [Services: VintedHunterService, .run_hunt()](Services-_VintedHunterService,_.run_hunt.md) (3 shared connections)
- [Scripts: seed_logistics(), seed_logistics.py](Scripts-_seed_logistics,_seed_logistics.py.md) (3 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (3 shared connections)

## Source Files

- `scripts/check_rules_db.py`
- `scripts/diagnostics/check_scoring.py`
- `scripts/maintenance/repair_opportunity_scores.py`
- `scripts/restore_cloud.py`
- `scripts/restore_intelligence.py`
- `scripts/test_cart_calc.py`
- `scripts/test_logistics_scenarios.py`
- `scripts/verify_logistics.py`
- `src/application/services/budget_optimizer_service.py`
- `src/application/services/currency_service.py`
- `src/application/services/logistics_service.py`
- `src/domain/models.py`
- `src/interfaces/api/routers/dashboard.py`
- `src/interfaces/api/routers/products.py`
- `tests/integration/test_logistics_and_pricing.py`
- `tests/unit/test_budget_optimizer.py`
- `tests/unit/test_market_analytics.py`

## Audit Trail

- EXTRACTED: 214 (76%)
- INFERRED: 68 (24%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*