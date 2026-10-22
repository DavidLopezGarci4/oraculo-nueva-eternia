# Routers: UserModel, system.py

> 46 nodes

## Key Concepts

- **UserModel** (129 connections) — `src/domain/models.py`
- **system.py** (33 connections) — `src/interfaces/api/routers/system.py`
- **telegram_listener.py** (30 connections) — `src/infrastructure/services/telegram_listener.py`
- **test_tcg_layouts_api.py** (18 connections) — `tests/unit/test_tcg_layouts_api.py`
- **AuthorizedDeviceModel** (16 connections) — `src/domain/models.py`
- **SystemConfigModel** (14 connections) — `src/domain/models.py`
- **is_telegram_only_missing_enabled()** (10 connections) — `src/application/services/telegram_filter_service.py`
- **should_send_product_push()** (10 connections) — `src/application/services/telegram_filter_service.py`
- **telegram_filter_service.py** (10 connections) — `src/application/services/telegram_filter_service.py`
- **save_tcg_layouts()** (9 connections) — `src/interfaces/api/routers/system.py`
- **set_telegram_only_missing_enabled()** (8 connections) — `src/application/services/telegram_filter_service.py`
- **get_tcg_layouts()** (7 connections) — `src/interfaces/api/routers/system.py`
- **run_maintenance()** (7 connections) — `src/interfaces/api/routers/system.py`
- **system_audit()** (7 connections) — `src/interfaces/api/routers/system.py`
- **update_telegram_config()** (7 connections) — `src/interfaces/api/routers/system.py`
- **save_sword_configs()** (6 connections) — `src/interfaces/api/routers/system.py`
- **test_save_tcg_layouts_non_admin()** (6 connections) — `tests/unit/test_tcg_layouts_api.py`
- **test_update_telegram_config_non_admin_forbidden()** (6 connections) — `tests/unit/test_tcg_layouts_api.py`
- **get_public_showcase()** (5 connections) — `src/interfaces/api/routers/showcase.py`
- **get_sword_configs()** (5 connections) — `src/interfaces/api/routers/system.py`
- **test_get_tcg_layouts_empty()** (5 connections) — `tests/unit/test_tcg_layouts_api.py`
- **test_save_tcg_layouts_admin_success()** (5 connections) — `tests/unit/test_tcg_layouts_api.py`
- **get_telegram_config()** (4 connections) — `src/interfaces/api/routers/system.py`
- **check_db_users.py** (4 connections) — `scripts/diagnostics/check_db_users.py`
- **get** (4 connections)
- *... and 21 more nodes in this community*

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (43 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (24 shared connections)
- [Core: auth.py, SecurityShield](Core-_auth.py,_SecurityShield.md) (20 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (19 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (14 shared connections)
- [Routers: admin.py, post](Routers-_admin.py,_post.md) (9 shared connections)
- [Services: routers/collection.py, GuardianService](Services-_routers-collection.py,_GuardianService.md) (9 shared connections)
- [Routers: lore.py, LoreHarvesterService](Routers-_lore.py,_LoreHarvesterService.md) (8 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (7 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (6 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (5 shared connections)
- [Services: .process_callback_query(), .get_user_status()](Services-_.process_callback_query,_.get_user_status.md) (4 shared connections)

## Source Files

- `scripts/diagnostics/check_db_users.py`
- `scripts/diagnostics/verify_phase0.py`
- `src/application/services/telegram_filter_service.py`
- `src/domain/models.py`
- `src/infrastructure/services/telegram_listener.py`
- `src/interfaces/api/routers/showcase.py`
- `src/interfaces/api/routers/system.py`
- `tests/unit/test_tcg_layouts_api.py`

## Audit Trail

- EXTRACTED: 210 (69%)
- INFERRED: 94 (31%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*