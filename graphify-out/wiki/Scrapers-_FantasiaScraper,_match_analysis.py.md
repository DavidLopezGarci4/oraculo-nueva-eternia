# Scrapers: FantasiaScraper, match_analysis.py

> 22 nodes

## Key Concepts

- **FantasiaScraper** (26 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **match_analysis.py** (12 connections) — `src/infrastructure/scrapers/match_analysis.py`
- **.search()** (8 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **._search_playwright()** (7 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **._extract_from_json_ld()** (6 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **._parse_html_item()** (6 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **test_reliability()** (5 connections) — `scripts/test_fantasia_reliability.py`
- **._parse_product_page()** (5 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **analyze_matches()** (5 connections) — `src/infrastructure/scrapers/match_analysis.py`
- **test_fantasia_manual.py** (5 connections) — `dev_tools/test_fantasia_manual.py`
- **._handle_popups()** (4 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **._scrape_detail()** (4 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **._parse_json_product()** (3 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **test_manual()** (2 connections) — `dev_tools/test_fantasia_manual.py`
- **Page** (2 connections)
- **clean_name()** (1 connections) — `src/infrastructure/scrapers/match_analysis.py`
- **BeautifulSoup** (1 connections)
- **Scraper for Fantasia Personajes (PrestaShop). Uses fast curl-cffi impersonation…** (1 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **Attempts to parse schema.org JSON-LD data. Looking for @type: ItemList or list…** (1 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **Fantasia specific: Extract EAN/Referencia.** (1 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **Fantasia specific: Close the 'LOGÍSTICA REYES' modal and accept cookies.** (1 connections) — `src/infrastructure/scrapers/fantasia_scraper.py`
- **scrapers_fantasiapersonajes** (1 connections)

## Relationships

- [Scrapers: ScrapedOffer, ._log()](Scrapers-_ScrapedOffer,_._log.md) (13 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (9 shared connections)
- [Scrapers: scrapers.py, run_scraper_task()](Scrapers-_scrapers.py,_run_scraper_task.md) (5 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (4 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (3 shared connections)
- [Scrapers: AmazonScraper, run_single.py](Scrapers-_AmazonScraper,_run_single.py.md) (2 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (2 shared connections)
- [Scrapers: ScrapingPipeline, test_scraper_interface.py](Scrapers-_ScrapingPipeline,_test_scraper_interface.py.md) (1 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (1 shared connections)
- [Core: brain_engine.py, .calculate_match()](Core-_brain_engine.py,_.calculate_match.md) (1 shared connections)

## Source Files

- `dev_tools/test_fantasia_manual.py`
- `scripts/test_fantasia_reliability.py`
- `src/infrastructure/scrapers/fantasia_scraper.py`
- `src/infrastructure/scrapers/match_analysis.py`

## Audit Trail

- EXTRACTED: 69 (93%)
- INFERRED: 5 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*