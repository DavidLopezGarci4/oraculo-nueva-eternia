# Routers: MarketAnalyticsService, analytics.py

> 47 nodes

## Key Concepts

- **MarketAnalyticsService** (27 connections) — `src/application/services/market_analytics_service.py`
- **analytics.py** (18 connections) — `src/interfaces/api/routers/analytics.py`
- **TestMarketAnalyticsEMI** (10 connections) — `tests/test_market_analytics.py`
- **domain/schemas.py** (10 connections) — `src/domain/schemas.py`
- **.get_market_index()** (9 connections) — `src/application/services/market_analytics_service.py`
- **pydantic** (8 connections)
- **.get_retail_scarcity_alerts()** (6 connections) — `src/application/services/market_analytics_service.py`
- **optimize_cart_budget()** (6 connections) — `src/interfaces/api/routers/analytics.py`
- **.get_delta_updates()** (5 connections) — `src/application/services/market_analytics_service.py`
- **.get_p2p_liquidity_pulse()** (5 connections) — `src/application/services/market_analytics_service.py`
- **get_liquidity_pulse()** (5 connections) — `src/interfaces/api/routers/analytics.py`
- **get_market_index()** (5 connections) — `src/interfaces/api/routers/analytics.py`
- **get_retail_scarcity()** (5 connections) — `src/interfaces/api/routers/analytics.py`
- **get_sync_delta_updates()** (5 connections) — `src/interfaces/api/routers/analytics.py`
- **test_delta_updates_catalog()** (5 connections) — `tests/unit/test_market_analytics.py`
- **test_market_index_calculation()** (5 connections) — `tests/unit/test_market_analytics.py`
- **test_p2p_liquidity_pulse_classifies_velocity_and_stagnant_bargains()** (5 connections) — `tests/unit/test_market_analytics.py`
- **CollectionItemBase** (4 connections) — `src/domain/schemas.py`
- **ProductBase** (4 connections) — `src/domain/schemas.py`
- **.test_compacted_only_product_contributes_to_emi_via_monthly_stats()** (4 connections) — `tests/test_market_analytics.py`
- **Any** (4 connections)
- **get** (4 connections)
- **test_market_index_quantitative.py** (4 connections) — `tests/unit/test_market_index_quantitative.py`
- **ProductSchema** (3 connections) — `src/domain/schemas.py`
- **BudgetOptimizeRequest** (3 connections) — `src/interfaces/api/routers/analytics.py`
- *... and 22 more nodes in this community*

## Relationships

- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (18 shared connections)
- [Services: LogisticsService, LogisticRuleModel](Services-_LogisticsService,_LogisticRuleModel.md) (13 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (5 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (4 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (4 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (3 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (2 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (1 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (1 shared connections)
- [Routers: lore.py, LoreHarvesterService](Routers-_lore.py,_LoreHarvesterService.md) (1 shared connections)
- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (1 shared connections)

## Source Files

- `src/application/services/market_analytics_service.py`
- `src/domain/schemas.py`
- `src/interfaces/api/routers/analytics.py`
- `tests/test_market_analytics.py`
- `tests/unit/test_market_analytics.py`
- `tests/unit/test_market_index_quantitative.py`

## Audit Trail

- EXTRACTED: 103 (82%)
- INFERRED: 22 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*