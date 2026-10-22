# Routers: OfferModel, json

> 126 nodes

## Key Concepts

- **OfferModel** (136 connections) — `src/domain/models.py`
- **json** (100 connections)
- **PendingMatchModel** (97 connections) — `src/domain/models.py`
- **purgatory.py** (72 connections) — `src/interfaces/api/routers/purgatory.py`
- **OfferHistoryModel** (53 connections) — `src/domain/models.py`
- **ProductAliasModel** (44 connections) — `src/domain/models.py`
- **ProductRepository** (41 connections) — `src/infrastructure/repositories/product.py`
- **BlackcludedItemModel** (37 connections) — `src/domain/models.py`
- **.update_database()** (30 connections) — `src/infrastructure/scrapers/pipeline.py`
- **VintageMiscellaneousModel** (23 connections) — `src/domain/models.py`
- **VintageProductModel** (23 connections) — `src/domain/models.py`
- **normalize_url()** (22 connections) — `src/core/url_utils.py`
- **migrate_purgatory_vintage.py** (21 connections) — `scripts/migrate_purgatory_vintage.py`
- **product.py** (21 connections) — `src/infrastructure/repositories/product.py`
- **test_revert_logistics.py** (19 connections) — `tests/unit/test_revert_logistics.py`
- **run_match_bulk_task()** (17 connections) — `src/interfaces/api/routers/purgatory.py`
- **run_match_task()** (16 connections) — `src/interfaces/api/routers/purgatory.py`
- **smoke_test.py** (16 connections) — `src/application/jobs/smoke_test.py`
- **migrate_existing_vintage()** (15 connections) — `scripts/migrate_purgatory_vintage.py`
- **clean_purgatory_globally()** (15 connections) — `src/infrastructure/scrapers/pipeline.py`
- **revert_action()** (15 connections) — `src/interfaces/api/routers/dashboard.py`
- **run_match_vintage_task()** (15 connections) — `src/interfaces/api/routers/purgatory.py`
- **import_wallapop_products()** (15 connections) — `src/interfaces/api/routers/users.py`
- **match_service.py** (15 connections) — `src/application/services/match_service.py`
- **restore_from_vault()** (14 connections) — `src/application/jobs/restore_vault.py`
- *... and 101 more nodes in this community*

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (104 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (83 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (58 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (37 shared connections)
- [Services: LogisticsService, LogisticRuleModel](Services-_LogisticsService,_LogisticRuleModel.md) (35 shared connections)
- [Scrapers: ScrapingPipeline, test_scraper_interface.py](Scrapers-_ScrapingPipeline,_test_scraper_interface.py.md) (20 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (19 shared connections)
- [Unit: PriceAlertModel, revert_vintage_to_purgatory.py](Unit-_PriceAlertModel,_revert_vintage_to_purgatory.py.md) (17 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (16 shared connections)
- [Services: dashboard.py, ValuationService](Services-_dashboard.py,_ValuationService.md) (15 shared connections)
- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (15 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (14 shared connections)

## Source Files

- `scripts/check_p2p_stats.py`
- `scripts/cleanup_last_matches.py`
- `scripts/delete_fictional_vintage.py`
- `scripts/diagnostics/verify_phase2.py`
- `scripts/fix_existing_vintage_offers.py`
- `scripts/migrate_purgatory_vintage.py`
- `scripts/rollback_european_scrapers.py`
- `scripts/test_unlink.py`
- `scripts/verify_sentinel.py`
- `src/application/jobs/data_recovery.py`
- `src/application/jobs/restore_vault.py`
- `src/application/jobs/smoke_test.py`
- `src/application/services/auditor.py`
- `src/application/services/deal_scorer.py`
- `src/application/services/match_service.py`
- `src/application/services/sentinel.py`
- `src/core/url_utils.py`
- `src/domain/models.py`
- `src/infrastructure/repositories/product.py`
- `src/infrastructure/scrapers/pipeline.py`

## Audit Trail

- EXTRACTED: 722 (74%)
- INFERRED: 260 (26%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*