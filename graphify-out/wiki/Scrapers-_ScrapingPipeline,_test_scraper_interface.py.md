# Scrapers: ScrapingPipeline, test_scraper_interface.py

> 38 nodes

## Key Concepts

- **ScrapingPipeline** (56 connections) — `src/infrastructure/scrapers/pipeline.py`
- **test_scraper_interface.py** (24 connections) — `tests/unit/test_scraper_interface.py`
- **scrape_wallapop_via_cdp.py** (11 connections) — `scripts/scrape_wallapop_via_cdp.py`
- **ScraperPlugin** (9 connections) — `src/infrastructure/scrapers/interface.py`
- **repro_pipeline_v2.py** (8 connections) — `scripts/experimental/repro_pipeline_v2.py`
- **ingest_json.py** (8 connections) — `src/application/jobs/ingest_json.py`
- **_harvest_tab()** (6 connections) — `scripts/scrape_wallapop_via_cdp.py`
- **ingest_data()** (5 connections) — `src/application/jobs/ingest_json.py`
- **TestPipelineHardening** (4 connections) — `scripts/experimental/repro_pipeline_v2.py`
- **.test_standardization()** (4 connections) — `scripts/experimental/repro_pipeline_v2.py`
- **_normalize_price()** (4 connections) — `scripts/scrape_wallapop_via_cdp.py`
- **interface.py** (4 connections) — `src/infrastructure/scrapers/interface.py`
- **main()** (3 connections) — `scripts/scrape_wallapop_via_cdp.py`
- **.search()** (3 connections) — `src/infrastructure/scrapers/interface.py`
- **.__init__()** (3 connections) — `src/infrastructure/scrapers/pipeline.py`
- **test_scraper_interface_imports()** (3 connections) — `tests/unit/test_scraper_interface.py`
- **.is_active()** (2 connections) — `src/infrastructure/scrapers/interface.py`
- **.name()** (2 connections) — `src/infrastructure/scrapers/interface.py`
- **.clean_product_name()** (2 connections) — `src/infrastructure/scrapers/pipeline.py`
- **._log()** (2 connections) — `src/infrastructure/scrapers/pipeline.py`
- **test_models_product_offer_alias()** (2 connections) — `tests/unit/test_scraper_interface.py`
- **test_scrape_multi_via_cdp_inner_imports()** (2 connections) — `tests/unit/test_scraper_interface.py`
- **test_scrape_multi_via_cdp_module_loads()** (2 connections) — `tests/unit/test_scraper_interface.py`
- **test_sync_availability_handles_timezone_aware_last_seen()** (2 connections) — `tests/unit/test_scraper_interface.py`
- **test_sync_availability_preserves_vintage_offers()** (2 connections) — `tests/unit/test_scraper_interface.py`
- *... and 13 more nodes in this community*

## Relationships

- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (20 shared connections)
- [Scrapers: ScrapedOffer, ._log()](Scrapers-_ScrapedOffer,_._log.md) (16 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (16 shared connections)
- [Scrapers: AmazonScraper, run_single.py](Scrapers-_AmazonScraper,_run_single.py.md) (7 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (6 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (4 shared connections)
- [Scrapers: SmythsToysScraper, ._parse_html()](Scrapers-_SmythsToysScraper,_._parse_html.md) (3 shared connections)
- [Services: VintedHunterService, .run_hunt()](Services-_VintedHunterService,_.run_hunt.md) (3 shared connections)
- [Scrapers: WallapopManualScraper, nexus_local_worker.py](Scrapers-_WallapopManualScraper,_nexus_local_worker.py.md) (3 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (3 shared connections)
- [Scrapers: scrapers.py, run_scraper_task()](Scrapers-_scrapers.py,_run_scraper_task.md) (2 shared connections)
- [Routers: wallapop_jobs.py, WallapopJobModel](Routers-_wallapop_jobs.py,_WallapopJobModel.md) (2 shared connections)

## Source Files

- `scripts/experimental/repro_pipeline_v2.py`
- `scripts/scrape_wallapop_via_cdp.py`
- `src/application/jobs/ingest_json.py`
- `src/infrastructure/scrapers/interface.py`
- `src/infrastructure/scrapers/pipeline.py`
- `tests/unit/test_scraper_interface.py`

## Audit Trail

- EXTRACTED: 114 (81%)
- INFERRED: 27 (19%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*