# Scrapers: AmazonScraper, run_single.py

> 32 nodes

## Key Concepts

- **AmazonScraper** (23 connections) — `src/infrastructure/scrapers/amazon_scraper.py`
- **run_single.py** (21 connections) — `src/infrastructure/scrapers/run_single.py`
- **VintedScraper** (20 connections) — `src/infrastructure/scrapers/vinted_scraper.py`
- **run_single_incursion.py** (16 connections) — `scripts/run_single_incursion.py`
- **run_scraper()** (15 connections) — `src/infrastructure/scrapers/run_single.py`
- **get_scraper_class()** (11 connections) — `scripts/run_single_incursion.py`
- **test_incursion_runner.py** (9 connections) — `tests/unit/test_incursion_runner.py`
- **execute_scraper()** (8 connections) — `scripts/run_single_incursion.py`
- **.search()** (8 connections) — `src/infrastructure/scrapers/amazon_scraper.py`
- **test_pipeline.py** (7 connections) — `src/infrastructure/scrapers/test_pipeline.py`
- **test_vinted.py** (7 connections) — `tests/scripts/test_vinted.py`
- **.search()** (6 connections) — `src/infrastructure/scrapers/vinted_scraper.py`
- **test_amazon_scraper_zero_cost_cascade()** (5 connections) — `tests/unit/test_free_scrapers_cascade.py`
- **main()** (4 connections) — `scripts/run_single_incursion.py`
- **run_sequential_incursion()** (4 connections) — `scripts/run_single_incursion.py`
- **.run_product_search()** (4 connections) — `src/infrastructure/scrapers/pipeline.py`
- **test_pipeline()** (4 connections) — `src/infrastructure/scrapers/test_pipeline.py`
- **._init_session()** (4 connections) — `src/infrastructure/scrapers/vinted_scraper.py`
- **test()** (3 connections) — `src/infrastructure/scrapers/amazon_scraper.py`
- **run()** (3 connections) — `tests/scripts/test_vinted.py`
- **test_execute_scraper_failure_resilience()** (3 connections) — `tests/unit/test_incursion_runner.py`
- **test_execute_scraper_success()** (3 connections) — `tests/unit/test_incursion_runner.py`
- **test_amazon_extraction()** (2 connections) — `scripts/diagnostics/diagnose_amazon_v2.py`
- **test_get_scraper_class()** (2 connections) — `tests/unit/test_incursion_runner.py`
- **asyncio** (2 connections)
- *... and 7 more nodes in this community*

## Relationships

- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (23 shared connections)
- [Scrapers: ScrapedOffer, ._log()](Scrapers-_ScrapedOffer,_._log.md) (15 shared connections)
- [Scrapers: scrapers.py, run_scraper_task()](Scrapers-_scrapers.py,_run_scraper_task.md) (8 shared connections)
- [Scrapers: wallapop_scraper.py, WallapopScraper](Scrapers-_wallapop_scraper.py,_WallapopScraper.md) (8 shared connections)
- [Scrapers: ScrapingPipeline, test_scraper_interface.py](Scrapers-_ScrapingPipeline,_test_scraper_interface.py.md) (7 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (6 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (4 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (4 shared connections)
- [Services: VintedHunterService, .run_hunt()](Services-_VintedHunterService,_.run_hunt.md) (3 shared connections)
- [Scrapers: SmythsToysScraper, ._parse_html()](Scrapers-_SmythsToysScraper,_._parse_html.md) (2 shared connections)
- [Scrapers: FantasiaScraper, match_analysis.py](Scrapers-_FantasiaScraper,_match_analysis.py.md) (2 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (2 shared connections)

## Source Files

- `scripts/diagnostics/diagnose_amazon_v2.py`
- `scripts/run_single_incursion.py`
- `src/infrastructure/scrapers/amazon_scraper.py`
- `src/infrastructure/scrapers/pipeline.py`
- `src/infrastructure/scrapers/run_single.py`
- `src/infrastructure/scrapers/test_pipeline.py`
- `src/infrastructure/scrapers/vinted_scraper.py`
- `tests/scripts/test_vinted.py`
- `tests/unit/test_free_scrapers_cascade.py`
- `tests/unit/test_incursion_runner.py`

## Audit Trail

- EXTRACTED: 128 (87%)
- INFERRED: 19 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*