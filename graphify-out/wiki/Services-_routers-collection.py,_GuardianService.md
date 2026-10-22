# Services: routers/collection.py, GuardianService

> 26 nodes

## Key Concepts

- **routers/collection.py** (33 connections) — `src/interfaces/api/routers/collection.py`
- **GuardianService** (18 connections) — `src/application/services/guardian_service.py`
- **ProductOutput** (7 connections) — `src/interfaces/api/schemas.py`
- **get_collection()** (7 connections) — `src/interfaces/api/routers/collection.py`
- **toggle_collection()** (7 connections) — `src/interfaces/api/routers/collection.py`
- **trigger_excel_sync_background()** (7 connections) — `src/interfaces/api/routers/collection.py`
- **update_collection_item()** (7 connections) — `src/interfaces/api/routers/collection.py`
- **.export_collection_to_excel()** (6 connections) — `src/application/services/guardian_service.py`
- **.export_vintage_collection_to_excel()** (6 connections) — `src/application/services/guardian_service.py`
- **sync_excel_from_db()** (5 connections) — `scripts/sync_excel_from_db.py`
- **.export_collection_to_sqlite()** (5 connections) — `src/application/services/guardian_service.py`
- **export_excel()** (5 connections) — `src/interfaces/api/routers/collection.py`
- **export_excel_vintage()** (5 connections) — `src/interfaces/api/routers/collection.py`
- **export_sqlite()** (5 connections) — `src/interfaces/api/routers/collection.py`
- **Session** (5 connections)
- **.restore_from_json()** (4 connections) — `src/application/services/guardian_service.py`
- **get** (4 connections)
- **fastapi_responses** (3 connections)
- **BackgroundTasks** (2 connections)
- **patch** (1 connections)
- **post** (1 connections)
- **Updates the 'Adquirido' column in the Excel file based on the status_map. Uses…** (1 connections) — `scripts/sync_excel_from_db.py`
- **Generates a fresh Excel export of the user's collection. If it's David, it…** (1 connections) — `src/application/services/guardian_service.py`
- **Generates a fresh Excel export of the user's Vintage collection. If it's David,…** (1 connections) — `src/application/services/guardian_service.py`
- **Generates a SQLite vault for the user using VaultService.** (1 connections) — `src/application/services/guardian_service.py`
- *... and 1 more nodes in this community*

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (17 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (9 shared connections)
- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (8 shared connections)
- [Services: vault.py, VaultService](Services-_vault.py,_VaultService.md) (7 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (7 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (6 shared connections)
- [Services: NexusService, .sync_catalog()](Services-_NexusService,_.sync_catalog.md) (3 shared connections)
- [Services: dashboard.py, ValuationService](Services-_dashboard.py,_ValuationService.md) (2 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (2 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (1 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (1 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (1 shared connections)

## Source Files

- `scripts/sync_excel_from_db.py`
- `src/application/services/guardian_service.py`
- `src/interfaces/api/routers/collection.py`
- `src/interfaces/api/schemas.py`

## Audit Trail

- EXTRACTED: 76 (72%)
- INFERRED: 30 (28%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*