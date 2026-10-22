# Dev_tools: sys, run_daily_scan()

> 55 nodes

## Key Concepts

- **sys** (91 connections)
- **run_daily_scan()** (42 connections) — `src/application/jobs/daily_scan.py`
- **io** (20 connections)
- **logger.py** (19 connections) — `src/core/logger.py`
- **setup_logging()** (13 connections) — `src/core/logger.py`
- **simulate_daily_scan.py** (12 connections) — `scripts/experimental/simulate_daily_scan.py`
- **BackupManager** (11 connections) — `src/core/backup_manager.py`
- **sync_nexus.py** (9 connections) — `scripts/sync_nexus.py`
- **sync_nexus_vintage.py** (9 connections) — `scripts/sync_nexus_vintage.py`
- **AuditLogger** (8 connections) — `src/core/audit_logger.py`
- **sync_external.py** (8 connections) — `src/application/jobs/sync_external.py`
- **diagnose_idealo.py** (7 connections) — `scripts/diagnostics/diagnose_idealo.py`
- **simulate()** (6 connections) — `scripts/experimental/simulate_daily_scan.py`
- **dev_tools/diagnose_amazon_v2.py** (6 connections) — `dev_tools/diagnose_amazon_v2.py`
- **test_telegram.py** (6 connections) — `scripts/test_telegram.py`
- **diagnose_kidinn.py** (5 connections) — `dev_tools/diagnose_kidinn.py`
- **verify_tradeinn_final.py** (5 connections) — `dev_tools/verify_tradeinn_final.py`
- **verify_tradeinn_final_specific.py** (5 connections) — `dev_tools/verify_tradeinn_final_specific.py`
- **verify_tradeinn_interactive.py** (5 connections) — `dev_tools/verify_tradeinn_interactive.py`
- **verify_tradeinn_legitimized.py** (5 connections) — `dev_tools/verify_tradeinn_legitimized.py`
- **verify_tradeinn_two_phase.py** (5 connections) — `dev_tools/verify_tradeinn_two_phase.py`
- **compact_price_history.py** (5 connections) — `scripts/compact_price_history.py`
- **force_run.py** (5 connections) — `src/infrastructure/scrapers/force_run.py`
- **MockScraper** (4 connections) — `scripts/diagnostics/diagnose_idealo.py`
- **main()** (4 connections) — `scripts/compact_price_history.py`
- *... and 30 more nodes in this community*

## Relationships

- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (58 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (41 shared connections)
- [Scrapers: scrapers.py, run_scraper_task()](Scrapers-_scrapers.py,_run_scraper_task.md) (12 shared connections)
- [Services: NexusService, .sync_catalog()](Services-_NexusService,_.sync_catalog.md) (11 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (7 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (7 shared connections)
- [Scrapers: ScrapedOffer, ._log()](Scrapers-_ScrapedOffer,_._log.md) (6 shared connections)
- [Scrapers: AmazonScraper, run_single.py](Scrapers-_AmazonScraper,_run_single.py.md) (6 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (5 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (4 shared connections)
- [Scrapers: ScrapingPipeline, test_scraper_interface.py](Scrapers-_ScrapingPipeline,_test_scraper_interface.py.md) (4 shared connections)
- [Services: VintedHunterService, .run_hunt()](Services-_VintedHunterService,_.run_hunt.md) (4 shared connections)

## Source Files

- `dev_tools/diagnose_amazon_v2.py`
- `dev_tools/diagnose_kidinn.py`
- `dev_tools/verify_tradeinn_final.py`
- `dev_tools/verify_tradeinn_final_specific.py`
- `dev_tools/verify_tradeinn_interactive.py`
- `dev_tools/verify_tradeinn_legitimized.py`
- `dev_tools/verify_tradeinn_two_phase.py`
- `scripts/compact_price_history.py`
- `scripts/diagnostics/diagnose_idealo.py`
- `scripts/experimental/simulate_daily_scan.py`
- `scripts/ox3_shield.py`
- `scripts/sync_nexus.py`
- `scripts/sync_nexus_vintage.py`
- `scripts/test_telegram.py`
- `src/application/jobs/daily_scan.py`
- `src/application/jobs/sync_external.py`
- `src/core/audit_logger.py`
- `src/core/backup_manager.py`
- `src/core/logger.py`
- `src/infrastructure/scrapers/force_run.py`

## Audit Trail

- EXTRACTED: 278 (95%)
- INFERRED: 16 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*