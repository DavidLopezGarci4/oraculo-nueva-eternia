# Services: NexusService, .sync_catalog()

> 43 nodes

## Key Concepts

- **NexusService** (26 connections) — `src/application/services/nexus_service.py`
- **.sync_catalog()** (18 connections) — `src/application/services/nexus_service.py`
- **StorageService** (15 connections) — `src/application/services/storage_service.py`
- **.sync_catalog()** (13 connections) — `src/application/services/nexus_vintage_service.py`
- **CatalogRefreshService** (9 connections) — `src/application/services/catalog_refresh_service.py`
- **.refresh_figure_image()** (8 connections) — `src/application/services/catalog_refresh_service.py`
- **TelemetryHandler** (6 connections) — `src/application/services/nexus_service.py`
- **TelemetryHandler** (6 connections) — `src/application/services/nexus_vintage_service.py`
- **.backup_stock()** (6 connections) — `src/application/services/guardian_service.py`
- **.ensure_bucket()** (5 connections) — `src/application/services/storage_service.py`
- **.upload_image()** (5 connections) — `src/application/services/storage_service.py`
- **refresh_product_image()** (5 connections) — `src/interfaces/api/routers/products.py`
- **run_nexus.py** (5 connections) — `scripts/run_nexus.py`
- **run_final_sync()** (4 connections) — `scripts/final_sync_origins.py`
- **run_nuclear_sync()** (4 connections) — `scripts/trigger_origins_refresh.py`
- **.purge_catalog()** (4 connections) — `src/application/services/nexus_service.py`
- **._get_safe_error_message()** (4 connections) — `src/application/services/storage_service.py`
- **trigger_nexus()** (3 connections) — `scripts/run_nexus.py`
- **.purge_catalog()** (3 connections) — `src/application/services/nexus_vintage_service.py`
- **.upload_all_local_images()** (3 connections) — `src/application/services/storage_service.py`
- **.find_af411_detail_url()** (2 connections) — `src/application/services/catalog_refresh_service.py`
- **run_migration_task()** (2 connections) — `src/application/services/nexus_service.py`
- **run_migration_task()** (2 connections) — `src/application/services/nexus_vintage_service.py`
- **post** (2 connections)
- **.emit()** (1 connections) — `src/application/services/nexus_service.py`
- *... and 18 more nodes in this community*

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (14 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (11 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (11 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (7 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (5 shared connections)
- [Services: routers/collection.py, GuardianService](Services-_routers-collection.py,_GuardianService.md) (3 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (3 shared connections)
- [Services: TelegramListener, .process_message()](Services-_TelegramListener,_.process_message.md) (2 shared connections)
- [Routers: admin.py, post](Routers-_admin.py,_post.md) (2 shared connections)
- [Scrapers: AmazonScraper, run_single.py](Scrapers-_AmazonScraper,_run_single.py.md) (2 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (1 shared connections)

## Source Files

- `scripts/final_sync_origins.py`
- `scripts/run_nexus.py`
- `scripts/trigger_origins_refresh.py`
- `src/application/services/catalog_refresh_service.py`
- `src/application/services/guardian_service.py`
- `src/application/services/nexus_service.py`
- `src/application/services/nexus_vintage_service.py`
- `src/application/services/storage_service.py`
- `src/interfaces/api/routers/products.py`

## Audit Trail

- EXTRACTED: 90 (75%)
- INFERRED: 30 (25%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*