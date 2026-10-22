# Scrapers: scrapers.py, run_scraper_task()

> 79 nodes

## Key Concepts

- **scrapers.py** (61 connections) — `src/interfaces/api/routers/scrapers.py`
- **run_scraper_task()** (28 connections) — `src/interfaces/api/routers/scrapers.py`
- **.__init__()** (21 connections) — `src/infrastructure/scrapers/base.py`
- **ElectropolisScraper** (17 connections) — `src/infrastructure/scrapers/electropolis_scraper.py`
- **FrikimazScraper** (16 connections) — `src/infrastructure/scrapers/frikimaz_scraper.py`
- **FrikiversoScraper** (16 connections) — `src/infrastructure/scrapers/frikiverso_scraper.py`
- **PixelatoyScraper** (15 connections) — `src/infrastructure/scrapers/pixelatoy_scraper.py`
- **ToymiEUScraper** (14 connections) — `src/infrastructure/scrapers/toymi_scraper.py`
- **DeToyboysNLScraper** (13 connections) — `src/infrastructure/scrapers/detoyboys_scraper.py`
- **profile_scraper.py** (13 connections) — `src/application/jobs/profile_scraper.py`
- **Time4ActionToysDEScraper** (11 connections) — `src/infrastructure/scrapers/time4actiontoys_scraper.py`
- **BixotoScraper** (10 connections) — `src/infrastructure/scrapers/bixoto_scraper.py`
- **profile()** (6 connections) — `src/application/jobs/profile_scraper.py`
- **.search()** (6 connections) — `src/infrastructure/scrapers/pixelatoy_scraper.py`
- **evaluate_frikimaz.py** (6 connections) — `src/infrastructure/scrapers/evaluate_frikimaz.py`
- **get** (6 connections)
- **test_frikiverso_manual.py** (5 connections) — `dev_tools/test_frikiverso_manual.py`
- **._scrape_detail()** (4 connections) — `src/infrastructure/scrapers/electropolis_scraper.py`
- **._handle_popups()** (4 connections) — `src/infrastructure/scrapers/frikiverso_scraper.py`
- **._scrape_detail()** (4 connections) — `src/infrastructure/scrapers/frikiverso_scraper.py`
- **._handle_popups()** (4 connections) — `src/infrastructure/scrapers/pixelatoy_scraper.py`
- **._parse_html_item()** (4 connections) — `src/infrastructure/scrapers/pixelatoy_scraper.py`
- **._scrape_detail()** (4 connections) — `src/infrastructure/scrapers/pixelatoy_scraper.py`
- **._set_country_spain()** (4 connections) — `src/infrastructure/scrapers/toymi_scraper.py`
- **download_wallapop_ip_logs()** (4 connections) — `src/interfaces/api/routers/scrapers.py`
- *... and 54 more nodes in this community*

## Relationships

- [Scrapers: ScrapedOffer, ._log()](Scrapers-_ScrapedOffer,_._log.md) (47 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (44 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (12 shared connections)
- [Scrapers: AmazonScraper, run_single.py](Scrapers-_AmazonScraper,_run_single.py.md) (8 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (8 shared connections)
- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (8 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (6 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (6 shared connections)
- [Scrapers: FantasiaScraper, match_analysis.py](Scrapers-_FantasiaScraper,_match_analysis.py.md) (5 shared connections)
- [Routers: stop_scrapers(), import_wallapop_manual_html()](Routers-_stop_scrapers,_import_wallapop_manual_html.md) (5 shared connections)
- [Services: GitHubQuotaService, github_quota_service.py](Services-_GitHubQuotaService,_github_quota_service.py.md) (5 shared connections)
- [Scrapers: wallapop_scraper.py, WallapopScraper](Scrapers-_wallapop_scraper.py,_WallapopScraper.md) (4 shared connections)

## Source Files

- `dev_tools/test_frikiverso_manual.py`
- `src/application/jobs/profile_scraper.py`
- `src/infrastructure/scrapers/amazon_scraper.py`
- `src/infrastructure/scrapers/base.py`
- `src/infrastructure/scrapers/bbts_scraper.py`
- `src/infrastructure/scrapers/bixoto_scraper.py`
- `src/infrastructure/scrapers/detoyboys_scraper.py`
- `src/infrastructure/scrapers/dvdstorespain_scraper.py`
- `src/infrastructure/scrapers/ebay_scraper.py`
- `src/infrastructure/scrapers/electropolis_scraper.py`
- `src/infrastructure/scrapers/evaluate_frikimaz.py`
- `src/infrastructure/scrapers/fantasia_scraper.py`
- `src/infrastructure/scrapers/frikimaz_scraper.py`
- `src/infrastructure/scrapers/frikiverso_scraper.py`
- `src/infrastructure/scrapers/lamansiondelterror_scraper.py`
- `src/infrastructure/scrapers/pixelatoy_scraper.py`
- `src/infrastructure/scrapers/smythstoys_scraper.py`
- `src/infrastructure/scrapers/time4actiontoys_scraper.py`
- `src/infrastructure/scrapers/toymi_scraper.py`
- `src/infrastructure/scrapers/tradeinn_scraper.py`

## Audit Trail

- EXTRACTED: 266 (94%)
- INFERRED: 18 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*