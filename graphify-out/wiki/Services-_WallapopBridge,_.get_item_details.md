# Services: WallapopBridge, .get_item_details()

> 8 nodes

## Key Concepts

- **WallapopBridge** (8 connections) — `src/application/services/wallapop_bridge.py`
- **.get_item_details()** (6 connections) — `src/application/services/wallapop_bridge.py`
- **.cmd_import_wallapop()** (6 connections) — `src/infrastructure/services/telegram_listener.py`
- **get_wallapop_preview()** (4 connections) — `src/interfaces/api/routers/products.py`
- **._get_headers()** (2 connections) — `src/application/services/wallapop_bridge.py`
- **Any** (1 connections)
- **Bridge service to interact with Wallapop internal API for detailed item…** (1 connections) — `src/application/services/wallapop_bridge.py`
- **Extracts item ID from URL and fetches full details from Wallapop API.** (1 connections) — `src/application/services/wallapop_bridge.py`

## Relationships

- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (3 shared connections)
- [Services: TelegramListener, .process_message()](Services-_TelegramListener,_.process_message.md) (3 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (2 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (1 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (1 shared connections)
- [Unit: validate_motu_relevance(), test_api_motu_relevance.py](Unit-_validate_motu_relevance,_test_api_motu_relevance.py.md) (1 shared connections)

## Source Files

- `src/application/services/wallapop_bridge.py`
- `src/infrastructure/services/telegram_listener.py`
- `src/interfaces/api/routers/products.py`

## Audit Trail

- EXTRACTED: 18 (90%)
- INFERRED: 2 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*