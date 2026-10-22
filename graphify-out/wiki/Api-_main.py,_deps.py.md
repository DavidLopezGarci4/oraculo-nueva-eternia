# Api: main.py, deps.py

> 51 nodes

## Key Concepts

- **main.py** (46 connections) — `src/interfaces/api/main.py`
- **deps.py** (41 connections) — `src/interfaces/api/deps.py`
- **users.py** (39 connections) — `src/interfaces/api/routers/users.py`
- **FastAPI** (22 connections)
- **logistics.py** (15 connections) — `src/interfaces/api/routers/logistics.py`
- **scope_user_id()** (13 connections) — `src/interfaces/api/deps.py`
- **verify_api_key()** (13 connections) — `src/interfaces/api/deps.py`
- **verify_device()** (11 connections) — `src/interfaces/api/deps.py`
- **cards.py** (10 connections) — `src/interfaces/api/routers/cards.py`
- **get_current_user()** (9 connections) — `src/interfaces/api/deps.py`
- **lifespan()** (9 connections) — `src/interfaces/api/main.py`
- **get_p2p_opportunities()** (8 connections) — `src/interfaces/api/routers/users.py`
- **api_calculate_cart()** (7 connections) — `src/interfaces/api/routers/logistics.py`
- **db_session()** (5 connections) — `tests/integration/test_phase0_migration.py`
- **_user_from_token()** (5 connections) — `src/interfaces/api/deps.py`
- **update_user_image_paths()** (5 connections) — `src/interfaces/api/routers/users.py`
- **UserImagePathsUpdateRequest** (4 connections) — `src/interfaces/api/schemas.py`
- **ensure_scrapers_registered()** (4 connections) — `src/interfaces/api/deps.py`
- **verify_wallapop_import()** (4 connections) — `src/interfaces/api/deps.py`
- **get_static_image_override()** (4 connections) — `src/interfaces/api/main.py`
- **get_user_settings()** (4 connections) — `src/interfaces/api/routers/users.py`
- **update_user_location()** (4 connections) — `src/interfaces/api/routers/users.py`
- **update_user_showcase()** (4 connections) — `src/interfaces/api/routers/users.py`
- **post** (4 connections)
- **jwt** (4 connections)
- *... and 26 more nodes in this community*

## Relationships

- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (24 shared connections)
- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (16 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (16 shared connections)
- [Core: auth.py, SecurityShield](Core-_auth.py,_SecurityShield.md) (13 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (12 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (11 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (8 shared connections)
- [Routers: lore.py, LoreHarvesterService](Routers-_lore.py,_LoreHarvesterService.md) (7 shared connections)
- [Services: routers/collection.py, GuardianService](Services-_routers-collection.py,_GuardianService.md) (6 shared connections)
- [Services: LogisticsService, LogisticRuleModel](Services-_LogisticsService,_LogisticRuleModel.md) (6 shared connections)
- [Routers: MarketAnalyticsService, analytics.py](Routers-_MarketAnalyticsService,_analytics.py.md) (5 shared connections)
- [Services: dashboard.py, ValuationService](Services-_dashboard.py,_ValuationService.md) (5 shared connections)

## Source Files

- `src/core/config.py`
- `src/interfaces/api/deps.py`
- `src/interfaces/api/main.py`
- `src/interfaces/api/routers/__init__.py`
- `src/interfaces/api/routers/cards.py`
- `src/interfaces/api/routers/health.py`
- `src/interfaces/api/routers/logistics.py`
- `src/interfaces/api/routers/users.py`
- `src/interfaces/api/schemas.py`
- `tests/integration/test_phase0_migration.py`

## Audit Trail

- EXTRACTED: 227 (92%)
- INFERRED: 20 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*