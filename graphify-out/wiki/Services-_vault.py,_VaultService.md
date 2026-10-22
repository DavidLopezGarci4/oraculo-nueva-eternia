# Services: vault.py, VaultService

> 33 nodes

## Key Concepts

- **vault.py** (25 connections) — `src/interfaces/api/routers/vault.py`
- **VaultService** (12 connections) — `src/application/services/vault_service.py`
- **ExcelManager** (11 connections) — `src/application/services/excel_manager.py`
- **StatusMessageOutput** (10 connections) — `src/interfaces/api/schemas.py`
- **.sync_acquisitions_from_db()** (6 connections) — `src/application/services/excel_manager.py`
- **api_stage_vault()** (6 connections) — `src/interfaces/api/routers/vault.py`
- **download_images_zip()** (6 connections) — `src/interfaces/api/routers/vault.py`
- **StagedImportModel** (5 connections) — `src/domain/models.py`
- **success()** (5 connections) — `src/core/logger.py`
- **api_sync_excel()** (5 connections) — `src/interfaces/api/routers/vault.py`
- **.generate_user_vault()** (4 connections) — `src/application/services/vault_service.py`
- **_resolve_staged_file()** (4 connections) — `src/interfaces/api/routers/vault.py`
- **._create_backup()** (3 connections) — `src/application/services/excel_manager.py`
- **.export_full_backup()** (3 connections) — `src/application/services/excel_manager.py`
- **api_generate_vault()** (3 connections) — `src/interfaces/api/routers/vault.py`
- **.stage_vault_import()** (2 connections) — `src/application/services/vault_service.py`
- **get** (2 connections)
- **post** (2 connections)
- **zipfile** (2 connections)
- **.__init__()** (1 connections) — `src/application/services/excel_manager.py`
- **.__init__()** (1 connections) — `src/application/services/vault_service.py`
- **slugify()** (1 connections) — `src/interfaces/api/routers/vault.py`
- **Session** (1 connections)
- **Path** (1 connections)
- **Gestor del Excel Bridge para sincronización de inventario. Mantiene el Excel…** (1 connections) — `src/application/services/excel_manager.py`
- *... and 8 more nodes in this community*

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (9 shared connections)
- [Services: routers/collection.py, GuardianService](Services-_routers-collection.py,_GuardianService.md) (7 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (3 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (3 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (3 shared connections)
- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (3 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (3 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (3 shared connections)
- [Core: auth.py, SecurityShield](Core-_auth.py,_SecurityShield.md) (2 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (2 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (1 shared connections)
- [Routers: admin.py, post](Routers-_admin.py,_post.md) (1 shared connections)

## Source Files

- `src/application/services/excel_manager.py`
- `src/application/services/vault_service.py`
- `src/core/logger.py`
- `src/domain/models.py`
- `src/interfaces/api/routers/vault.py`
- `src/interfaces/api/schemas.py`

## Audit Trail

- EXTRACTED: 74 (86%)
- INFERRED: 12 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*