# Scripts: ScraperStatusModel, ScraperExecutionLogModel

> 27 nodes

## Key Concepts

- **ScraperStatusModel** (44 connections) — `src/domain/models.py`
- **ScraperExecutionLogModel** (40 connections) — `src/domain/models.py`
- **Base** (31 connections) — `src/domain/base.py`
- **NexusVintageService** (16 connections) — `src/application/services/nexus_vintage_service.py`
- **migrate_data()** (11 connections) — `scripts/migrate_to_cloud.py`
- **cleanup_decommissioned_shops.py** (9 connections) — `scripts/cleanup_decommissioned_shops.py`
- **cleanup_harvester.py** (7 connections) — `scripts/cleanup_harvester.py`
- **cleanup_idealo.py** (7 connections) — `scripts/cleanup_idealo.py`
- **cloud_db_check.py** (6 connections) — `scripts/diagnostics/cloud_db_check.py`
- **cleanup_duplicates.py** (5 connections) — `scripts/cleanup_duplicates.py`
- **cleanup_dvd_low.py** (5 connections) — `scripts/cleanup_dvd_low.py`
- **init_scrapers_cloud.py** (5 connections) — `scripts/maintenance/init_scrapers_cloud.py`
- **init_db()** (4 connections) — `src/infrastructure/database.py`
- **rename_tradeinn.py** (4 connections) — `dev_tools/rename_tradeinn.py`
- **cleanup_shops()** (3 connections) — `scripts/cleanup_decommissioned_shops.py`
- **check_db()** (3 connections) — `scripts/diagnostics/cloud_db_check.py`
- **diag_db.py** (3 connections) — `scripts/diag_db.py`
- **rename_scraper()** (2 connections) — `dev_tools/rename_tradeinn.py`
- **cleanup_duplicates()** (2 connections) — `scripts/cleanup_duplicates.py`
- **cleanup_specific_duplicates()** (2 connections) — `scripts/cleanup_dvd_low.py`
- **clean_harvester()** (2 connections) — `scripts/cleanup_harvester.py`
- **clean_idealo()** (2 connections) — `scripts/cleanup_idealo.py`
- **initialize_scrapers()** (2 connections) — `scripts/maintenance/init_scrapers_cloud.py`
- **DeclarativeBase** (1 connections)
- **Migrates data from local SQLite to Target PostgreSQL.** (1 connections) — `scripts/migrate_to_cloud.py`
- *... and 2 more nodes in this community*

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (40 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (14 shared connections)
- [Services: NexusService, .sync_catalog()](Services-_NexusService,_.sync_catalog.md) (11 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (10 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (9 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (7 shared connections)
- [Scrapers: scrapers.py, run_scraper_task()](Scrapers-_scrapers.py,_run_scraper_task.md) (6 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (5 shared connections)
- [Services: GitHubQuotaService, github_quota_service.py](Services-_GitHubQuotaService,_github_quota_service.py.md) (5 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (5 shared connections)
- [Integration: test_api_response_schemas.py, test_scrapers_status_logs_ip_logs_match_schema()](Integration-_test_api_response_schemas.py,_test_scrapers_status_logs_ip_logs_match_schema.md) (4 shared connections)
- [Routers: stop_scrapers(), import_wallapop_manual_html()](Routers-_stop_scrapers,_import_wallapop_manual_html.md) (4 shared connections)

## Source Files

- `dev_tools/rename_tradeinn.py`
- `scripts/cleanup_decommissioned_shops.py`
- `scripts/cleanup_duplicates.py`
- `scripts/cleanup_dvd_low.py`
- `scripts/cleanup_harvester.py`
- `scripts/cleanup_idealo.py`
- `scripts/diag_db.py`
- `scripts/diagnostics/cloud_db_check.py`
- `scripts/maintenance/init_scrapers_cloud.py`
- `scripts/migrate_to_cloud.py`
- `src/application/services/nexus_vintage_service.py`
- `src/domain/base.py`
- `src/domain/models.py`
- `src/infrastructure/database.py`

## Audit Trail

- EXTRACTED: 132 (74%)
- INFERRED: 47 (26%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*