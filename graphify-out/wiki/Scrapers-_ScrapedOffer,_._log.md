# Scrapers: ScrapedOffer, ._log()

> 90 nodes

## Key Concepts

- **ScrapedOffer** (144 connections) — `src/infrastructure/scrapers/base.py`
- **._log()** (40 connections) — `src/infrastructure/scrapers/base.py`
- **EbayScraper** (24 connections) — `src/infrastructure/scrapers/ebay_scraper.py`
- **._normalize_price()** (23 connections) — `src/infrastructure/scrapers/base.py`
- **._safe_navigate()** (20 connections) — `src/infrastructure/scrapers/base.py`
- **DVDStoreSpainScraper** (17 connections) — `src/infrastructure/scrapers/dvdstorespain_scraper.py`
- **._get_random_header()** (17 connections) — `src/infrastructure/scrapers/base.py`
- **LaMansionDelTerrorScraper** (15 connections) — `src/infrastructure/scrapers/lamansiondelterror_scraper.py`
- **._curl_get()** (15 connections) — `src/infrastructure/scrapers/base.py`
- **TriguetechScraper** (12 connections) — `src/infrastructure/scrapers/triguetech_scraper.py`
- **._random_sleep()** (11 connections) — `src/infrastructure/scrapers/base.py`
- **.search()** (11 connections) — `src/infrastructure/scrapers/dvdstorespain_scraper.py`
- **._sirius_a1_human_search()** (8 connections) — `src/infrastructure/scrapers/amazon_scraper.py`
- **._run_search_session()** (8 connections) — `src/infrastructure/scrapers/ebay_scraper.py`
- **.search()** (8 connections) — `src/infrastructure/scrapers/ebay_scraper.py`
- **._scrape_all_pages_playwright()** (8 connections) — `src/infrastructure/scrapers/frikimaz_scraper.py`
- **._scrape_all_pages_playwright()** (8 connections) — `src/infrastructure/scrapers/lamansiondelterror_scraper.py`
- **._fast_infiltration()** (7 connections) — `src/infrastructure/scrapers/amazon_scraper.py`
- **.search()** (7 connections) — `src/infrastructure/scrapers/bixoto_scraper.py`
- **.search()** (7 connections) — `src/infrastructure/scrapers/detoyboys_scraper.py`
- **._parse_product_page()** (7 connections) — `src/infrastructure/scrapers/dvdstorespain_scraper.py`
- **._sitemap_search()** (7 connections) — `src/infrastructure/scrapers/dvdstorespain_scraper.py`
- **._extract_page_items()** (7 connections) — `src/infrastructure/scrapers/ebay_scraper.py`
- **._scrape_all_pages_curl()** (7 connections) — `src/infrastructure/scrapers/frikimaz_scraper.py`
- **._scrape_all_pages_curl()** (7 connections) — `src/infrastructure/scrapers/lamansiondelterror_scraper.py`
- *... and 65 more nodes in this community*

## Relationships

- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (61 shared connections)
- [Scrapers: scrapers.py, run_scraper_task()](Scrapers-_scrapers.py,_run_scraper_task.md) (47 shared connections)
- [Scrapers: SmythsToysScraper, ._parse_html()](Scrapers-_SmythsToysScraper,_._parse_html.md) (20 shared connections)
- [Scrapers: ScrapingPipeline, test_scraper_interface.py](Scrapers-_ScrapingPipeline,_test_scraper_interface.py.md) (16 shared connections)
- [Scrapers: AmazonScraper, run_single.py](Scrapers-_AmazonScraper,_run_single.py.md) (15 shared connections)
- [Scrapers: FantasiaScraper, match_analysis.py](Scrapers-_FantasiaScraper,_match_analysis.py.md) (13 shared connections)
- [Scrapers: wallapop_scraper.py, WallapopScraper](Scrapers-_wallapop_scraper.py,_WallapopScraper.md) (8 shared connections)
- [Services: VintedHunterService, .run_hunt()](Services-_VintedHunterService,_.run_hunt.md) (6 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (6 shared connections)
- [Scrapers: tradeinn_scraper.py, TradeinnScraper](Scrapers-_tradeinn_scraper.py,_TradeinnScraper.md) (5 shared connections)
- [Scrapers: WallapopManualScraper, nexus_local_worker.py](Scrapers-_WallapopManualScraper,_nexus_local_worker.py.md) (5 shared connections)
- [Scrapers: adapter.py, Scraper3OXAdapter](Scrapers-_adapter.py,_Scraper3OXAdapter.md) (3 shared connections)

## Source Files

- `scripts/audits/verify_ebay_enhancements.py`
- `scripts/experimental/repro_pipeline.py`
- `scripts/test_jitter.py`
- `src/infrastructure/scrapers/amazon_scraper.py`
- `src/infrastructure/scrapers/base.py`
- `src/infrastructure/scrapers/bbts_scraper.py`
- `src/infrastructure/scrapers/bixoto_scraper.py`
- `src/infrastructure/scrapers/detoyboys_scraper.py`
- `src/infrastructure/scrapers/dvdstorespain_scraper.py`
- `src/infrastructure/scrapers/ebay_scraper.py`
- `src/infrastructure/scrapers/electropolis_scraper.py`
- `src/infrastructure/scrapers/evaluate_dvdstorespain.py`
- `src/infrastructure/scrapers/evaluate_lamansiondelterror.py`
- `src/infrastructure/scrapers/frikimaz_scraper.py`
- `src/infrastructure/scrapers/frikiverso_scraper.py`
- `src/infrastructure/scrapers/lamansiondelterror_scraper.py`
- `src/infrastructure/scrapers/time4actiontoys_scraper.py`
- `src/infrastructure/scrapers/toymi_scraper.py`
- `src/infrastructure/scrapers/triguetech_scraper.py`

## Audit Trail

- EXTRACTED: 389 (91%)
- INFERRED: 39 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*