# Unit: PriceAlertModel, revert_vintage_to_purgatory.py

> 15 nodes

## Key Concepts

- **PriceAlertModel** (21 connections) — `src/domain/models.py`
- **revert_vintage_to_purgatory.py** (15 connections) — `scripts/revert_vintage_to_purgatory.py`
- **test_api_telegram_alerts.py** (13 connections) — `tests/unit/test_api_telegram_alerts.py`
- **check_and_send_multiuser_alerts()** (11 connections) — `src/infrastructure/scrapers/pipeline.py`
- **revert_vintage_to_purgatory()** (9 connections) — `scripts/revert_vintage_to_purgatory.py`
- **test_check_and_send_multiuser_alerts_price_alert()** (9 connections) — `tests/unit/test_api_telegram_alerts.py`
- **test_check_and_send_multiuser_alerts_wishlist()** (8 connections) — `tests/unit/test_api_telegram_alerts.py`
- **anyio_backend()** (2 connections) — `tests/unit/test_api_telegram_alerts.py`
- **mock_query()** (2 connections) — `tests/unit/test_api_telegram_alerts.py`
- **anyio** (2 connections)
- **Session** (2 connections)
- **mock_query()** (1 connections) — `tests/unit/test_api_telegram_alerts.py`
- **fixture** (1 connections)
- **Vigilancia de precios del Centinela.** (1 connections) — `src/domain/models.py`
- **Cruza una nueva oferta con las listas de deseos y alertas de precio de todos…** (1 connections) — `src/infrastructure/scrapers/pipeline.py`

## Relationships

- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (17 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (11 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (9 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (4 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (4 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (4 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (1 shared connections)
- [Core: NotifierService, ._should_throttle()](Core-_NotifierService,_._should_throttle.md) (1 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (1 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (1 shared connections)
- [Tests: conftest.py, unittest_mock](Tests-_conftest.py,_unittest_mock.md) (1 shared connections)

## Source Files

- `scripts/revert_vintage_to_purgatory.py`
- `src/domain/models.py`
- `src/infrastructure/scrapers/pipeline.py`
- `tests/unit/test_api_telegram_alerts.py`

## Audit Trail

- EXTRACTED: 52 (68%)
- INFERRED: 24 (32%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*