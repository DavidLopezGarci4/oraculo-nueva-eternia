# Scrapers: asyncio, logging

> 109 nodes

## Key Concepts

- **asyncio** (121 connections)
- **logging** (107 connections)
- **typing** (92 connections)
- **daily_scan.py** (75 connections) — `src/application/jobs/daily_scan.py`
- **BaseScraper** (62 connections) — `src/infrastructure/scrapers/base.py`
- **scrapers/base.py** (52 connections) — `src/infrastructure/scrapers/base.py`
- **re** (51 connections)
- **bs4** (39 connections)
- **playwright_async_api** (32 connections)
- **random** (26 connections)
- **smythstoys_scraper.py** (24 connections) — `src/infrastructure/scrapers/smythstoys_scraper.py`
- **amazon_scraper.py** (21 connections) — `src/infrastructure/scrapers/amazon_scraper.py`
- **scrape_multi_via_cdp.py** (19 connections) — `scripts/scrape_multi_via_cdp.py`
- **BigBadToyStoreScraper** (18 connections) — `src/infrastructure/scrapers/bbts_scraper.py`
- **wallapop_manual_scraper.py** (18 connections) — `src/infrastructure/scrapers/wallapop_manual_scraper.py`
- **wallapop_section_api.py** (18 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **vinted_scraper.py** (17 connections) — `src/infrastructure/scrapers/vinted_scraper.py`
- **wallapop_manual_importer.py** (17 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **wallapop_signed_api.py** (17 connections) — `src/infrastructure/scrapers/wallapop_signed_api.py`
- **ebay_scraper.py** (16 connections) — `src/infrastructure/scrapers/ebay_scraper.py`
- **simulated_connection.py** (16 connections) — `src/infrastructure/scrapers/simulated_connection.py`
- **fantasia_scraper.py** (14 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **bbts_scraper.py** (13 connections) — `src/infrastructure/scrapers/bbts_scraper.py`
- **dvdstorespain_scraper.py** (13 connections) — `src/infrastructure/scrapers/dvdstorespain_scraper.py`
- **gemini_card_service.py** (12 connections) — `src/application/services/gemini_card_service.py`
- *... and 84 more nodes in this community*

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (65 shared connections)
- [Scrapers: ScrapedOffer, ._log()](Scrapers-_ScrapedOffer,_._log.md) (61 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (58 shared connections)
- [Scrapers: scrapers.py, run_scraper_task()](Scrapers-_scrapers.py,_run_scraper_task.md) (44 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (37 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (34 shared connections)
- [Scrapers: wallapop_scraper.py, WallapopScraper](Scrapers-_wallapop_scraper.py,_WallapopScraper.md) (24 shared connections)
- [Scrapers: AmazonScraper, run_single.py](Scrapers-_AmazonScraper,_run_single.py.md) (23 shared connections)
- [Scrapers: ScrapingPipeline, test_scraper_interface.py](Scrapers-_ScrapingPipeline,_test_scraper_interface.py.md) (16 shared connections)
- [Collectors: personal_vintage_collection.py, time](Collectors-_personal_vintage_collection.py,_time.md) (14 shared connections)
- [Scripts: security.py, check_and_renew_ssl_gh_actions.py](Scripts-_security.py,_check_and_renew_ssl_gh_actions.py.md) (13 shared connections)
- [Routers: lore.py, LoreHarvesterService](Routers-_lore.py,_LoreHarvesterService.md) (12 shared connections)

## Source Files

- `dev_tools/analyze_frikiverso.py`
- `dev_tools/analyze_frikiverso_selectors.py`
- `dev_tools/motive_brute_force.py`
- `dev_tools/test_tradeinn.py`
- `dev_tools/test_tradeinn_pw.py`
- `dev_tools/test_tradeinn_pw_refined.py`
- `dev_tools/test_tradeinn_robust.py`
- `scripts/audits/audit_wallapop_fields.py`
- `scripts/diagnostics/diagnose_amazon_v2.py`
- `scripts/diagnostics/diagnose_shipping_fix.py`
- `scripts/experimental/extract_ebay_patterns.py`
- `scripts/final_sync_origins.py`
- `scripts/scrape_multi_via_cdp.py`
- `scripts/test_fantasia_reliability.py`
- `scripts/test_jitter.py`
- `scripts/trigger_origins_refresh.py`
- `src/application/jobs/daily_scan.py`
- `src/application/services/currency_service.py`
- `src/application/services/gemini_card_service.py`
- `src/application/services/wallapop_bridge.py`

## Audit Trail

- EXTRACTED: 933 (99%)
- INFERRED: 7 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*