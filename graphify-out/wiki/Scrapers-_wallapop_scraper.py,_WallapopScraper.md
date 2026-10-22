# Scrapers: wallapop_scraper.py, WallapopScraper

> 30 nodes

## Key Concepts

- **wallapop_scraper.py** (26 connections) — `src/infrastructure/scrapers/wallapop_scraper.py`
- **WallapopScraper** (25 connections) — `src/infrastructure/scrapers/wallapop_scraper.py`
- **WallapopIpLogModel** (15 connections) — `src/domain/models.py`
- **search_wallapop_v3_signed()** (14 connections) — `src/infrastructure/scrapers/wallapop_signed_api.py`
- **test_free_scrapers_cascade.py** (12 connections) — `tests/unit/test_free_scrapers_cascade.py`
- **.search_via_api()** (10 connections) — `src/infrastructure/scrapers/wallapop_scraper.py`
- **.search()** (7 connections) — `src/infrastructure/scrapers/wallapop_scraper.py`
- **._fetch_free_proxies()** (5 connections) — `src/infrastructure/scrapers/wallapop_scraper.py`
- **test_smythstoys_scraper_zero_cost_cascade()** (5 connections) — `tests/unit/test_free_scrapers_cascade.py`
- **test_wallapop_apify_rotation_fallback()** (5 connections) — `tests/unit/test_free_scrapers_cascade.py`
- **test_wallapop.py** (5 connections) — `tests/scripts/test_wallapop.py`
- **SignedSearchResult** (4 connections) — `src/infrastructure/scrapers/wallapop_signed_api.py`
- **_audit_ip_log()** (4 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **_audit_ip_log()** (4 connections) — `src/infrastructure/scrapers/wallapop_signed_api.py`
- **test()** (3 connections) — `src/infrastructure/scrapers/wallapop_scraper.py`
- **run()** (3 connections) — `tests/scripts/test_wallapop.py`
- **asyncio** (3 connections)
- **_log()** (1 connections) — `src/infrastructure/scrapers/wallapop_signed_api.py`
- **AsyncSession** (1 connections)
- **AsyncSession** (1 connections)
- **Historial de IPs y WAF checks de Wallapop para auditoría.** (1 connections) — `src/domain/models.py`
- **Intenta obtener las ofertas de Wallapop de forma directa y ultra-rápida.…** (1 connections) — `src/infrastructure/scrapers/wallapop_scraper.py`
- **Scraper de Wallapop Híbrido (API Directa / Apify / ScraperAPI / Playwright…** (1 connections) — `src/infrastructure/scrapers/wallapop_scraper.py`
- **Cosecha proxies públicos y frescos de Geonode y ProxyScrape de forma…** (1 connections) — `src/infrastructure/scrapers/wallapop_scraper.py`
- **Registra de forma best-effort el resultado de la incursión en…** (1 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- *... and 5 more nodes in this community*

## Relationships

- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (24 shared connections)
- [Unit: test_wallapop_signed_api.py, WallapopSigner](Unit-_test_wallapop_signed_api.py,_WallapopSigner.md) (9 shared connections)
- [Scrapers: AmazonScraper, run_single.py](Scrapers-_AmazonScraper,_run_single.py.md) (8 shared connections)
- [Scrapers: ScrapedOffer, ._log()](Scrapers-_ScrapedOffer,_._log.md) (8 shared connections)
- [Scrapers: scrapers.py, run_scraper_task()](Scrapers-_scrapers.py,_run_scraper_task.md) (4 shared connections)
- [Scrapers: search_wallapop_section(), test_wallapop_section_api.py](Scrapers-_search_wallapop_section,_test_wallapop_section_api.py.md) (4 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (3 shared connections)
- [Scrapers: SmythsToysScraper, ._parse_html()](Scrapers-_SmythsToysScraper,_._parse_html.md) (3 shared connections)
- [Integration: test_api_response_schemas.py, test_scrapers_status_logs_ip_logs_match_schema()](Integration-_test_api_response_schemas.py,_test_scrapers_status_logs_ip_logs_match_schema.md) (2 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (1 shared connections)
- [Scrapers: WallapopManualScraper, nexus_local_worker.py](Scrapers-_WallapopManualScraper,_nexus_local_worker.py.md) (1 shared connections)
- [Unit: test_search_wallapop_v3_signed_smoke(), network](Unit-_test_search_wallapop_v3_signed_smoke,_network.md) (1 shared connections)

## Source Files

- `src/domain/models.py`
- `src/infrastructure/scrapers/wallapop_scraper.py`
- `src/infrastructure/scrapers/wallapop_section_api.py`
- `src/infrastructure/scrapers/wallapop_signed_api.py`
- `tests/scripts/test_wallapop.py`
- `tests/unit/test_free_scrapers_cascade.py`

## Audit Trail

- EXTRACTED: 106 (90%)
- INFERRED: 12 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*