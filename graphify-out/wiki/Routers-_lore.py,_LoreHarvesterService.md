# Routers: lore.py, LoreHarvesterService

> 82 nodes

## Key Concepts

- **lore.py** (40 connections) — `src/interfaces/api/routers/lore.py`
- **LoreHarvesterService** (29 connections) — `src/application/services/lore_harvester_service.py`
- **CharacterLoreModel** (18 connections) — `src/domain/models.py`
- **ProductLoreSeedService** (14 connections) — `src/application/services/product_lore_seed.py`
- **lore_harvester_service.py** (14 connections) — `src/application/services/lore_harvester_service.py`
- **ProductLoreModel** (13 connections) — `src/domain/models.py`
- **.get_or_create_character_lore()** (13 connections) — `src/application/services/lore_harvester_service.py`
- **product_lore_seed.py** (13 connections) — `src/application/services/product_lore_seed.py`
- **.generate_default_lore_for_product()** (11 connections) — `src/application/services/product_lore_seed.py`
- **Session** (11 connections)
- **harvest_missing_lore()** (10 connections) — `src/interfaces/api/routers/lore.py`
- **list_product_lores()** (10 connections) — `src/interfaces/api/routers/lore.py`
- **update_product_lore()** (10 connections) — `src/interfaces/api/routers/lore.py`
- **test_lore_harvester.py** (10 connections) — `tests/unit/test_lore_harvester.py`
- **get_product_lore()** (9 connections) — `src/interfaces/api/routers/lore.py`
- **list_character_lore()** (9 connections) — `src/interfaces/api/routers/lore.py`
- **.harvest_for_product()** (8 connections) — `src/application/services/lore_harvester_service.py`
- **.resolve_character_slug()** (8 connections) — `src/application/services/lore_harvester_service.py`
- **harvest_lore()** (8 connections) — `src/interfaces/api/routers/lore.py`
- **seed_origins_lore()** (8 connections) — `src/interfaces/api/routers/lore.py`
- **update_character_lore()** (8 connections) — `src/interfaces/api/routers/lore.py`
- **BaseModel** (8 connections)
- **.update_character()** (7 connections) — `src/application/services/lore_harvester_service.py`
- **harvest_product_lore()** (7 connections) — `src/interfaces/api/routers/lore.py`
- **.seed_initial_catalog()** (6 connections) — `src/application/services/lore_harvester_service.py`
- *... and 57 more nodes in this community*

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (14 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (12 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (11 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (8 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (7 shared connections)
- [Services: TelegramListener, .process_message()](Services-_TelegramListener,_.process_message.md) (3 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (3 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (2 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (2 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (2 shared connections)
- [Routers: MarketAnalyticsService, analytics.py](Routers-_MarketAnalyticsService,_analytics.py.md) (1 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (1 shared connections)

## Source Files

- `src/application/services/lore_harvester_service.py`
- `src/application/services/product_lore_seed.py`
- `src/domain/models.py`
- `src/interfaces/api/routers/lore.py`
- `tests/unit/test_lore_harvester.py`

## Audit Trail

- EXTRACTED: 208 (84%)
- INFERRED: 39 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*