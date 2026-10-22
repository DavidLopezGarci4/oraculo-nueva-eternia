# Scripts: pandas, sqlite3

> 42 nodes

## Key Concepts

- **pandas** (42 connections)
- **sqlite3** (25 connections)
- **cloud_merge()** (7 connections) — `scripts/cloud_merge.py`
- **test_deduplication()** (6 connections) — `tests/integration/test_phase0_migration.py`
- **audit_catalogs.py** (6 connections) — `scripts/audit_catalogs.py`
- **detailed_audit.py** (6 connections) — `scripts/detailed_audit.py`
- **scripts/diagnostic_db.py** (5 connections) — `scripts/diagnostic_db.py`
- **restore_collection_status.py** (5 connections) — `scripts/restore_collection_status.py`
- **audit_backup.py** (4 connections) — `scripts/audit_backup.py`
- **check_catalog_diff.py** (4 connections) — `scripts/check_catalog_diff.py`
- **clean_excel.py** (4 connections) — `scripts/clean_excel.py`
- **emergency_recovery.py** (4 connections) — `scripts/emergency_recovery.py`
- **exhaustive_dump.py** (4 connections) — `scripts/exhaustive_dump.py`
- **audit_catalogs()** (3 connections) — `scripts/audit_catalogs.py`
- **find_diff()** (3 connections) — `scripts/check_catalog_diff.py`
- **cleanup()** (3 connections) — `scripts/cleanup_catalog.py`
- **detailed_audit()** (3 connections) — `scripts/detailed_audit.py`
- **sync()** (3 connections) — `scripts/maintenance/sync_to_cloud.py`
- **clean_acquired()** (3 connections) — `scripts/restore_collection_status.py`
- **restore_acquired_status()** (3 connections) — `scripts/restore_collection_status.py`
- **audit_deals.py** (3 connections) — `scripts/audit_deals.py`
- **count_excel_ids.py** (3 connections) — `scripts/count_excel_ids.py`
- **fix_source_type_schema.py** (3 connections) — `scripts/fix_source_type_schema.py`
- **migrate_deal_scorer.py** (3 connections) — `scripts/migrate_deal_scorer.py`
- **exhaustive_search()** (2 connections) — `scripts/audit_backup.py`
- *... and 17 more nodes in this community*

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (39 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (8 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (7 shared connections)
- [Collectors: personal_vintage_collection.py, time](Collectors-_personal_vintage_collection.py,_time.md) (5 shared connections)
- [Collectors: personal_collection.py, process_table()](Collectors-_personal_collection.py,_process_table.md) (4 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (3 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (1 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (1 shared connections)
- [Scripts: test_currency_logic.py, clean_price()](Scripts-_test_currency_logic.py,_clean_price.md) (1 shared connections)
- [Collectors: combine_sections(), make_key()](Collectors-_combine_sections,_make_key.md) (1 shared connections)
- [Services: LogisticsService, LogisticRuleModel](Services-_LogisticsService,_LogisticRuleModel.md) (1 shared connections)

## Source Files

- `scripts/audit_backup.py`
- `scripts/audit_catalogs.py`
- `scripts/audit_deals.py`
- `scripts/check_catalog_diff.py`
- `scripts/clean_excel.py`
- `scripts/cleanup_catalog.py`
- `scripts/cloud_merge.py`
- `scripts/count_excel_ids.py`
- `scripts/detailed_audit.py`
- `scripts/diagnostic_db.py`
- `scripts/diagnostics/check_alembic.py`
- `scripts/diagnostics/check_db_size.py`
- `scripts/diagnostics/check_local_product_cols.py`
- `scripts/diagnostics/check_local_users.py`
- `scripts/emergency_recovery.py`
- `scripts/exhaustive_dump.py`
- `scripts/fix_source_type_schema.py`
- `scripts/maintenance/sync_to_cloud.py`
- `scripts/migrate_deal_scorer.py`
- `scripts/restore_collection_status.py`

## Audit Trail

- EXTRACTED: 124 (95%)
- INFERRED: 6 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*