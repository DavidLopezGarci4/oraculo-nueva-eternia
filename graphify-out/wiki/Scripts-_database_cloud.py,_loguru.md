# Scripts: database_cloud.py, loguru

> 52 nodes

## Key Concepts

- **database_cloud.py** (101 connections) — `src/infrastructure/database_cloud.py`
- **loguru** (60 connections)
- **pipeline.py** (56 connections) — `src/infrastructure/scrapers/pipeline.py`
- **logistics_service.py** (30 connections) — `src/application/services/logistics_service.py`
- **DealScorer** (26 connections) — `src/application/services/deal_scorer.py`
- **vinted_hunter_service.py** (25 connections) — `src/application/services/vinted_hunter_service.py`
- **telegram_oracle_ai.py** (16 connections) — `src/application/services/telegram_oracle_ai.py`
- **deal_scorer.py** (15 connections) — `src/application/services/deal_scorer.py`
- **restore_intelligence.py** (13 connections) — `scripts/restore_intelligence.py`
- **telegram_service.py** (13 connections) — `src/infrastructure/services/telegram_service.py`
- **restore_cloud.py** (12 connections) — `scripts/restore_cloud.py`
- **repair_opportunity_scores.py** (11 connections) — `scripts/maintenance/repair_opportunity_scores.py`
- **check_scoring.py** (9 connections) — `scripts/diagnostics/check_scoring.py`
- **init_cloud_db()** (7 connections) — `src/infrastructure/database_cloud.py`
- **check_cloud_users.py** (7 connections) — `scripts/diagnostics/check_cloud_users.py`
- **sync_db_schema.py** (7 connections) — `scripts/sync_db_schema.py`
- **test_cart_api.py** (7 connections) — `scripts/test_cart_api.py`
- **seed_test_vintage.py** (6 connections) — `scripts/seed_test_vintage.py`
- **reassign_to_david.py** (6 connections) — `src/infrastructure/scripts/reassign_to_david.py`
- **fix_ebay_tags.py** (5 connections) — `scripts/fix_ebay_tags.py`
- **check_cloud_data()** (4 connections) — `scripts/diagnostics/check_cloud_users.py`
- **get_af411_link.py** (4 connections) — `scripts/experimental/get_af411_link.py`
- **get_wallapop_urls.py** (4 connections) — `scripts/experimental/get_wallapop_urls.py`
- **fix_collection_sequence.py** (4 connections) — `scripts/fix_collection_sequence.py`
- **fix_db_schema.py** (4 connections) — `scripts/maintenance/fix_db_schema.py`
- *... and 27 more nodes in this community*

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (76 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (58 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (34 shared connections)
- [Services: LogisticsService, LogisticRuleModel](Services-_LogisticsService,_LogisticRuleModel.md) (31 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (30 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (14 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (11 shared connections)
- [Services: VintedHunterService, .run_hunt()](Services-_VintedHunterService,_.run_hunt.md) (11 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (10 shared connections)
- [Scripts: pandas, sqlite3](Scripts-_pandas,_sqlite3.md) (8 shared connections)
- [Scrapers: ScrapingPipeline, test_scraper_interface.py](Scrapers-_ScrapingPipeline,_test_scraper_interface.py.md) (6 shared connections)
- [Core: auth.py, SecurityShield](Core-_auth.py,_SecurityShield.md) (5 shared connections)

## Source Files

- `scripts/diagnostics/check_cloud_users.py`
- `scripts/diagnostics/check_scoring.py`
- `scripts/diagnostics/physical_schema_check.py`
- `scripts/experimental/get_af411_link.py`
- `scripts/experimental/get_wallapop_urls.py`
- `scripts/fix_collection_sequence.py`
- `scripts/fix_ebay_tags.py`
- `scripts/maintenance/fix_db_schema.py`
- `scripts/maintenance/migrate_dna.py`
- `scripts/maintenance/repair_opportunity_scores.py`
- `scripts/migrate_cloud_scorer.py`
- `scripts/migrate_logistics.py`
- `scripts/migrate_phase39.py`
- `scripts/migrate_sentinel.py`
- `scripts/restore_cloud.py`
- `scripts/restore_intelligence.py`
- `scripts/seed_test_vintage.py`
- `scripts/sync_db_schema.py`
- `scripts/test_cart_api.py`
- `src/application/services/deal_scorer.py`

## Audit Trail

- EXTRACTED: 407 (95%)
- INFERRED: 20 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*