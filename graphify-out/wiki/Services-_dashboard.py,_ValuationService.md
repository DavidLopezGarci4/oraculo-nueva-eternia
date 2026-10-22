# Services: dashboard.py, ValuationService

> 19 nodes

## Key Concepts

- **dashboard.py** (41 connections) — `src/interfaces/api/routers/dashboard.py`
- **ValuationService** (17 connections) — `src/application/services/valuation_service.py`
- **get_dashboard_stats()** (7 connections) — `src/interfaces/api/routers/dashboard.py`
- **.get_collection_valuation()** (6 connections) — `src/application/services/valuation_service.py`
- **get_dashboard_hall_of_fame()** (6 connections) — `src/interfaces/api/routers/dashboard.py`
- **.get_consolidated_value()** (5 connections) — `src/application/services/valuation_service.py`
- **.get_pure_landed_value()** (5 connections) — `src/application/services/valuation_service.py`
- **get** (5 connections)
- **.get_condition_multiplier()** (3 connections) — `src/application/services/valuation_service.py`
- **.preload_offers_for_products()** (3 connections) — `src/application/services/valuation_service.py`
- **get_dashboard_history()** (3 connections) — `src/interfaces/api/routers/dashboard.py`
- **get_dashboard_match_stats()** (3 connections) — `src/interfaces/api/routers/dashboard.py`
- **.__init__()** (2 connections) — `src/application/services/valuation_service.py`
- **Session** (1 connections)
- **Calculates total value of a user's collection using the waterfall and legacy…** (1 connections) — `src/application/services/valuation_service.py`
- **Returns ONLY the landed value if a live offer exists (Retail or P2P). Used for…** (1 connections) — `src/application/services/valuation_service.py`
- **Pre-carga ofertas activas para optimizar consultas N+1 en loops.** (1 connections) — `src/application/services/valuation_service.py`
- **Implementation of the VALUATION WATERFALL. Returns the best possible market…** (1 connections) — `src/application/services/valuation_service.py`
- **Calculates the value multiplier based on condition and grade. Standard…** (1 connections) — `src/application/services/valuation_service.py`

## Relationships

- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (15 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (8 shared connections)
- [Services: LogisticsService, LogisticRuleModel](Services-_LogisticsService,_LogisticRuleModel.md) (8 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (6 shared connections)
- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (6 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (5 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (3 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (3 shared connections)
- [Services: routers/collection.py, GuardianService](Services-_routers-collection.py,_GuardianService.md) (2 shared connections)
- [Services: vault.py, VaultService](Services-_vault.py,_VaultService.md) (1 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (1 shared connections)

## Source Files

- `src/application/services/valuation_service.py`
- `src/interfaces/api/routers/dashboard.py`

## Audit Trail

- EXTRACTED: 68 (80%)
- INFERRED: 17 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*