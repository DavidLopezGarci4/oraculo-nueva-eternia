# Scripts: test_currency_logic.py, clean_price()

> 11 nodes

## Key Concepts

- **test_currency_logic.py** (8 connections) — `scripts/test_currency_logic.py`
- **clean_price()** (6 connections) — `scripts/phase0_migration.py`
- **clean_numeric()** (6 connections) — `src/infrastructure/collectors/personal_collection.py`
- **normalize_us_price()** (5 connections) — `scripts/phase0_migration.py`
- **extract_deep_intelligence()** (5 connections) — `src/infrastructure/collectors/personal_collection.py`
- **test_migration_logic()** (3 connections) — `scripts/test_currency_logic.py`
- **test_currency_detection()** (2 connections) — `scripts/test_currency_logic.py`
- **Limpia símbolos de moneda y convierte a float.** (1 connections) — `scripts/phase0_migration.py`
- **Normalizes a US Dollar value to Euro for comparison. Phase 10: Master Nexus…** (1 connections) — `scripts/phase0_migration.py`
- **Sanitiza strings de precios ($14.99, 14.99€, etc.) a (float, currency). Maneja…** (1 connections) — `src/infrastructure/collectors/personal_collection.py`
- **Extracts high-value identifiers and market sentiment from a product detail…** (1 connections) — `src/infrastructure/collectors/personal_collection.py`

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (5 shared connections)
- [Collectors: personal_collection.py, process_table()](Collectors-_personal_collection.py,_process_table.md) (4 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (2 shared connections)
- [Scripts: pandas, sqlite3](Scripts-_pandas,_sqlite3.md) (1 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (1 shared connections)

## Source Files

- `scripts/phase0_migration.py`
- `scripts/test_currency_logic.py`
- `src/infrastructure/collectors/personal_collection.py`

## Audit Trail

- EXTRACTED: 26 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*