# Scrapers: WallapopManualScraper, nexus_local_worker.py

> 18 nodes

## Key Concepts

- **WallapopManualScraper** (17 connections) — `src/infrastructure/scrapers/wallapop_manual_scraper.py`
- **nexus_local_worker.py** (14 connections) — `scripts/nexus_local_worker.py`
- **dotenv** (13 connections)
- **process_job()** (7 connections) — `scripts/nexus_local_worker.py`
- **.search()** (6 connections) — `src/infrastructure/scrapers/wallapop_manual_scraper.py`
- **._search_single()** (6 connections) — `src/infrastructure/scrapers/wallapop_manual_scraper.py`
- **main_loop()** (5 connections) — `scripts/nexus_local_worker.py`
- **._search_with_pagination()** (5 connections) — `src/infrastructure/scrapers/wallapop_manual_scraper.py`
- **claim_pending_job()** (3 connections) — `scripts/nexus_local_worker.py`
- **submit_results()** (3 connections) — `scripts/nexus_local_worker.py`
- **_test()** (3 connections) — `src/infrastructure/scrapers/wallapop_manual_scraper.py`
- **audit_supabase.py** (3 connections) — `scripts/audits/audit_supabase.py`
- **final_cloud_check.py** (3 connections) — `scripts/diagnostics/final_cloud_check.py`
- **.__init__()** (2 connections) — `src/infrastructure/scrapers/wallapop_manual_scraper.py`
- **AsyncSession** (2 connections)
- **psycopg2** (2 connections)
- **Nexus Local Bridge — Worker de Wallapop (IP Residencial). Fase 2 del plan…** (1 connections) — `scripts/nexus_local_worker.py`
- **Scraper de Wallapop basado en el endpoint orgánico /api/v3/search/section con…** (1 connections) — `src/infrastructure/scrapers/wallapop_manual_scraper.py`

## Relationships

- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (8 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (6 shared connections)
- [Scrapers: ScrapedOffer, ._log()](Scrapers-_ScrapedOffer,_._log.md) (5 shared connections)
- [Scrapers: SmythsToysScraper, ._parse_html()](Scrapers-_SmythsToysScraper,_._parse_html.md) (4 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (3 shared connections)
- [Scrapers: scrapers.py, run_scraper_task()](Scrapers-_scrapers.py,_run_scraper_task.md) (3 shared connections)
- [Scrapers: ScrapingPipeline, test_scraper_interface.py](Scrapers-_ScrapingPipeline,_test_scraper_interface.py.md) (3 shared connections)
- [Dev_tools: requests, analyze_411_structure.py](Dev_tools-_requests,_analyze_411_structure.py.md) (3 shared connections)
- [Collectors: personal_vintage_collection.py, time](Collectors-_personal_vintage_collection.py,_time.md) (2 shared connections)
- [Scrapers: wallapop_scraper.py, WallapopScraper](Scrapers-_wallapop_scraper.py,_WallapopScraper.md) (1 shared connections)
- [Scrapers: search_wallapop_section(), test_wallapop_section_api.py](Scrapers-_search_wallapop_section,_test_wallapop_section_api.py.md) (1 shared connections)
- [Scripts: security.py, check_and_renew_ssl_gh_actions.py](Scripts-_security.py,_check_and_renew_ssl_gh_actions.py.md) (1 shared connections)

## Source Files

- `scripts/audits/audit_supabase.py`
- `scripts/diagnostics/final_cloud_check.py`
- `scripts/nexus_local_worker.py`
- `src/infrastructure/scrapers/wallapop_manual_scraper.py`

## Audit Trail

- EXTRACTED: 64 (93%)
- INFERRED: 5 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*