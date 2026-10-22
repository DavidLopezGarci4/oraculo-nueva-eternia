# Core: NotifierService, ._should_throttle()

> 12 nodes

## Key Concepts

- **NotifierService** (14 connections) — `src/core/notifier.py`
- **._should_throttle()** (6 connections) — `src/core/notifier.py`
- **test_rate_limiting()** (4 connections) — `src/application/jobs/smoke_test.py`
- **.send_deal_alert_sync()** (3 connections) — `src/core/notifier.py`
- **.send_message()** (3 connections) — `src/core/notifier.py`
- **.check_price_alerts_sync()** (2 connections) — `src/core/notifier.py`
- **.send_deal_alert()** (2 connections) — `src/core/notifier.py`
- **.__init__()** (1 connections) — `src/core/notifier.py`
- **Session** (1 connections)
- **Generic message sender with anti-spam protection** (1 connections) — `src/core/notifier.py`
- **Returns True if the message should be throttled.** (1 connections) — `src/core/notifier.py`
- **Synchronous version for use in sync pipeline context** (1 connections) — `src/core/notifier.py`

## Relationships

- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (3 shared connections)
- [Scrapers: AmazonScraper, run_single.py](Scrapers-_AmazonScraper,_run_single.py.md) (2 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (1 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (1 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (1 shared connections)
- [Unit: PriceAlertModel, revert_vintage_to_purgatory.py](Unit-_PriceAlertModel,_revert_vintage_to_purgatory.py.md) (1 shared connections)

## Source Files

- `src/application/jobs/smoke_test.py`
- `src/core/notifier.py`

## Audit Trail

- EXTRACTED: 22 (92%)
- INFERRED: 2 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*