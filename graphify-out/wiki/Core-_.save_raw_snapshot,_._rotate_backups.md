# Core: .save_raw_snapshot(), ._rotate_backups()

> 6 nodes

## Key Concepts

- **.save_raw_snapshot()** (5 connections) — `src/core/backup_manager.py`
- **._rotate_backups()** (4 connections) — `src/core/backup_manager.py`
- **Any** (1 connections)
- **Path** (1 connections)
- **Saves the raw scraped data before any processing. Acts as the 'Flight Recorder'…** (1 connections) — `src/core/backup_manager.py`
- **Removes oldest files if limit exceeded.** (1 connections) — `src/core/backup_manager.py`

## Relationships

- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (2 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (1 shared connections)

## Source Files

- `src/core/backup_manager.py`

## Audit Trail

- EXTRACTED: 7 (88%)
- INFERRED: 1 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*