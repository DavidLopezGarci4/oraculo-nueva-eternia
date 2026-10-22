# Routers: ProductModel, products.py

> 70 nodes

## Key Concepts

- **ProductModel** (205 connections) — `src/domain/models.py`
- **products.py** (67 connections) — `src/interfaces/api/routers/products.py`
- **PriceHistoryModel** (36 connections) — `src/domain/models.py`
- **market_analytics_service.py** (19 connections) — `src/application/services/market_analytics_service.py`
- **MaintenanceService** (16 connections) — `src/application/services/maintenance_service.py`
- **ProductMonthlyStatsModel** (16 connections) — `src/domain/models.py`
- **MarketIntelligenceService** (15 connections) — `src/application/services/market_intelligence.py`
- **maintenance_service.py** (15 connections) — `src/application/services/maintenance_service.py`
- **get** (12 connections)
- **test_compactation.py** (12 connections) — `tests/test_compactation.py`
- **tests/test_market_analytics.py** (12 connections) — `tests/test_market_analytics.py`
- **verify_market_fixes.py** (11 connections) — `scripts/audits/verify_market_fixes.py`
- **market_intelligence.py** (11 connections) — `src/application/services/market_intelligence.py`
- **TestDatabaseCompactation** (9 connections) — `tests/test_compactation.py`
- **.compact_database()** (8 connections) — `src/application/services/maintenance_service.py`
- **get_products()** (8 connections) — `src/interfaces/api/routers/products.py`
- **bulk_stat_sync.py** (7 connections) — `scripts/maintenance/bulk_stat_sync.py`
- **verify_deal_scorer.py** (7 connections) — `scripts/verify_deal_scorer.py`
- **edit_product()** (6 connections) — `src/interfaces/api/routers/products.py`
- **get_purgatory_counts()** (6 connections) — `src/interfaces/api/routers/products.py`
- **.test_dynamic_periods_and_monthly_compacted_reuse_without_synthetic_sine()** (6 connections) — `tests/test_market_analytics.py`
- **cloud_seed()** (5 connections) — `scripts/cloud_seed.py`
- **verify_deal_scorer()** (5 connections) — `scripts/verify_deal_scorer.py`
- **.is_mandatory_buy()** (5 connections) — `src/application/services/deal_scorer.py`
- **get_temporary_products()** (5 connections) — `src/interfaces/api/routers/admin.py`
- *... and 45 more nodes in this community*

## Relationships

- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (83 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (79 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (30 shared connections)
- [Routers: MarketAnalyticsService, analytics.py](Routers-_MarketAnalyticsService,_analytics.py.md) (18 shared connections)
- [Services: LogisticsService, LogisticRuleModel](Services-_LogisticsService,_LogisticRuleModel.md) (17 shared connections)
- [Routers: lore.py, LoreHarvesterService](Routers-_lore.py,_LoreHarvesterService.md) (11 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (10 shared connections)
- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (10 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (9 shared connections)
- [Unit: PriceAlertModel, revert_vintage_to_purgatory.py](Unit-_PriceAlertModel,_revert_vintage_to_purgatory.py.md) (9 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (8 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (7 shared connections)

## Source Files

- `scripts/audits/verify_market_fixes.py`
- `scripts/cloud_seed.py`
- `scripts/diagnostics/check_af411.py`
- `scripts/diagnostics/check_products.py`
- `scripts/maintenance/bulk_stat_sync.py`
- `scripts/verify_deal_scorer.py`
- `src/application/services/deal_scorer.py`
- `src/application/services/maintenance_service.py`
- `src/application/services/market_analytics_service.py`
- `src/application/services/market_intelligence.py`
- `src/application/services/sentinel.py`
- `src/domain/models.py`
- `src/infrastructure/repositories/product.py`
- `src/interfaces/api/routers/admin.py`
- `src/interfaces/api/routers/products.py`
- `tests/integration/test_api_response_schemas.py`
- `tests/test_compactation.py`
- `tests/test_market_analytics.py`
- `tests/unit/test_scraper_interface.py`

## Audit Trail

- EXTRACTED: 378 (75%)
- INFERRED: 129 (25%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*