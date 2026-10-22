# Scripts: models.py, os

> 126 nodes

## Key Concepts

- **models.py** (159 connections) — `src/domain/models.py`
- **os** (131 connections)
- **CollectionItemModel** (94 connections) — `src/domain/models.py`
- **datetime** (72 connections)
- **sqlalchemy** (70 connections)
- **pathlib** (53 connections)
- **config.py** (46 connections) — `src/core/config.py`
- **sqlalchemy_orm** (44 connections)
- **nexus_service.py** (31 connections) — `src/application/services/nexus_service.py`
- **nexus_vintage_service.py** (26 connections) — `src/application/services/nexus_vintage_service.py`
- **phase0_migration.py** (25 connections) — `scripts/phase0_migration.py`
- **database.py** (23 connections) — `src/infrastructure/database.py`
- **restore_vault.py** (22 connections) — `src/application/jobs/restore_vault.py`
- **migrate_excel_to_db()** (21 connections) — `scripts/phase0_migration.py`
- **phase0_vintage_migration.py** (21 connections) — `scripts/phase0_vintage_migration.py`
- **migrate_to_cloud.py** (18 connections) — `scripts/migrate_to_cloud.py`
- **sync_excel_from_db.py** (18 connections) — `scripts/sync_excel_from_db.py`
- **catalog_refresh_service.py** (17 connections) — `src/application/services/catalog_refresh_service.py`
- **weight_engine.py** (17 connections) — `src/core/weight_engine.py`
- **backup_supabase.py** (16 connections) — `scripts/backup_supabase.py`
- **verify_phase0.py** (15 connections) — `scripts/diagnostics/verify_phase0.py`
- **vault_service.py** (15 connections) — `src/application/services/vault_service.py`
- **test_phase0_migration.py** (15 connections) — `tests/integration/test_phase0_migration.py`
- **cleanup_last_matches.py** (14 connections) — `scripts/cleanup_last_matches.py`
- **cloud_merge.py** (14 connections) — `scripts/cloud_merge.py`
- *... and 101 more nodes in this community*

## Relationships

- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (104 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (79 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (76 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (65 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (43 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (41 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (40 shared connections)
- [Scripts: pandas, sqlite3](Scripts-_pandas,_sqlite3.md) (39 shared connections)
- [Services: routers/collection.py, GuardianService](Services-_routers-collection.py,_GuardianService.md) (17 shared connections)
- [Services: LogisticsService, LogisticRuleModel](Services-_LogisticsService,_LogisticRuleModel.md) (17 shared connections)
- [Scripts: security.py, check_and_renew_ssl_gh_actions.py](Scripts-_security.py,_check_and_renew_ssl_gh_actions.py.md) (17 shared connections)
- [Versions: alembic, 66c2ec769424_initial_migration.py](Versions-_alembic,_66c2ec769424_initial_migration.py.md) (15 shared connections)

## Source Files

- `migrations/env.py`
- `scripts/analyze_deps.py`
- `scripts/backup_supabase.py`
- `scripts/cleanup_catalog.py`
- `scripts/cleanup_last_matches.py`
- `scripts/cloud_backup.py`
- `scripts/cloud_merge.py`
- `scripts/cloud_seed.py`
- `scripts/diagnostics/check_cloud_size.py`
- `scripts/diagnostics/check_collection_counts.py`
- `scripts/diagnostics/check_deals.py`
- `scripts/diagnostics/check_global_stats.py`
- `scripts/diagnostics/check_shop_dist.py`
- `scripts/diagnostics/check_users.py`
- `scripts/diagnostics/count_users.py`
- `scripts/diagnostics/diagnostic_db.py`
- `scripts/diagnostics/verify_phase0.py`
- `scripts/fix_sequences.py`
- `scripts/maintenance/sync_to_cloud.py`
- `scripts/manual_migration.py`

## Audit Trail

- EXTRACTED: 1050 (94%)
- INFERRED: 63 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*