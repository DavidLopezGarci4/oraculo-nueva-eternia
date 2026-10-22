# Services: VintedHunterService, .run_hunt()

> 59 nodes

## Key Concepts

- **VintedHunterService** (25 connections) — `src/application/services/vinted_hunter_service.py`
- **.run_hunt()** (20 connections) — `src/application/services/vinted_hunter_service.py`
- **test_vinted_hunter.py** (18 connections) — `tests/unit/test_vinted_hunter.py`
- **VintedSentinelService** (16 connections) — `src/application/services/vinted_sentinel_service.py`
- **SmartMatcher** (16 connections) — `src/core/matching.py`
- **vinted_sentinel_service.py** (11 connections) — `src/application/services/vinted_sentinel_service.py`
- **matching.py** (10 connections) — `src/core/matching.py`
- **test_vinted_sentinel.py** (9 connections) — `tests/unit/test_vinted_sentinel.py`
- **HunterAlertLogModel** (8 connections) — `src/domain/models.py`
- **hunt_vinted.py** (8 connections) — `scripts/hunt_vinted.py`
- **.dispatch_hunt()** (7 connections) — `src/application/services/vinted_sentinel_service.py`
- **test_vinted_hunter_deduplicates_same_day()** (7 connections) — `tests/unit/test_vinted_hunter.py`
- **test_vinted_hunter_skips_discarded_offers()** (7 connections) — `tests/unit/test_vinted_hunter.py`
- **benchmark_rapid_matching.py** (7 connections) — `scripts/diagnostics/benchmark_rapid_matching.py`
- **.match()** (6 connections) — `src/core/matching.py`
- **test_vinted_hunter_detects_bargain()** (6 connections) — `tests/unit/test_vinted_hunter.py`
- **test_vinted_hunter_discards_parts_and_damage()** (6 connections) — `tests/unit/test_vinted_hunter.py`
- **test_vinted_hunter_discards_sub_nine_euro_floor()** (6 connections) — `tests/unit/test_vinted_hunter.py`
- **test_sentinel_status_and_lifecycle()** (6 connections) — `tests/unit/test_vinted_sentinel.py`
- **rust_bridge.py** (6 connections) — `src/core/rust_bridge.py`
- **._is_daily_scan_blackout()** (5 connections) — `src/application/services/vinted_sentinel_service.py`
- **._sentinel_loop()** (5 connections) — `src/application/services/vinted_sentinel_service.py`
- **test_matcher_precision.py** (5 connections) — `tests/unit/test_matcher_precision.py`
- **test_specific_purgatory_cases.py** (5 connections) — `tests/unit/test_specific_purgatory_cases.py`
- **asyncio** (5 connections)
- *... and 34 more nodes in this community*

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (12 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (11 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (8 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (7 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (7 shared connections)
- [Scrapers: ScrapedOffer, ._log()](Scrapers-_ScrapedOffer,_._log.md) (6 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (4 shared connections)
- [Services: LogisticsService, LogisticRuleModel](Services-_LogisticsService,_LogisticRuleModel.md) (3 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (3 shared connections)
- [Scrapers: AmazonScraper, run_single.py](Scrapers-_AmazonScraper,_run_single.py.md) (3 shared connections)
- [Scrapers: ScrapingPipeline, test_scraper_interface.py](Scrapers-_ScrapingPipeline,_test_scraper_interface.py.md) (3 shared connections)
- [Tests: conftest.py, unittest_mock](Tests-_conftest.py,_unittest_mock.md) (3 shared connections)

## Source Files

- `scripts/diagnostics/benchmark_rapid_matching.py`
- `scripts/hunt_vinted.py`
- `src/application/services/vinted_hunter_service.py`
- `src/application/services/vinted_sentinel_service.py`
- `src/core/matching.py`
- `src/core/rust_bridge.py`
- `src/domain/models.py`
- `src/infrastructure/services/telegram_listener.py`
- `tests/unit/test_matcher_precision.py`
- `tests/unit/test_specific_purgatory_cases.py`
- `tests/unit/test_vinted_hunter.py`
- `tests/unit/test_vinted_sentinel.py`

## Audit Trail

- EXTRACTED: 145 (76%)
- INFERRED: 47 (24%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*