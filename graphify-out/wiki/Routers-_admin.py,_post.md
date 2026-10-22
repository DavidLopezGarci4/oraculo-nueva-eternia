# Routers: admin.py, post

> 25 nodes

## Key Concepts

- **admin.py** (49 connections) — `src/interfaces/api/routers/admin.py`
- **post** (8 connections)
- **authorize_device()** (6 connections) — `src/interfaces/api/routers/admin.py`
- **create_user()** (6 connections) — `src/interfaces/api/routers/admin.py`
- **renew_ssl()** (6 connections) — `src/interfaces/api/routers/admin.py`
- **get** (5 connections)
- **AnomalyValidationRequest** (4 connections) — `src/interfaces/api/schemas.py`
- **CreateUserRequest** (4 connections) — `src/interfaces/api/schemas.py`
- **SSLRenewRequest** (4 connections) — `src/interfaces/api/schemas.py`
- **UserRoleUpdateRequest** (4 connections) — `src/interfaces/api/schemas.py`
- **delete_hero()** (4 connections) — `src/interfaces/api/routers/admin.py`
- **get_all_heroes()** (4 connections) — `src/interfaces/api/routers/admin.py`
- **reset_smartmatches()** (4 connections) — `src/interfaces/api/routers/admin.py`
- **sync_nexus()** (4 connections) — `src/interfaces/api/routers/admin.py`
- **sync_nexus_vintage()** (4 connections) — `src/interfaces/api/routers/admin.py`
- **update_hero_role()** (4 connections) — `src/interfaces/api/routers/admin.py`
- **validate_anomaly()** (4 connections) — `src/interfaces/api/routers/admin.py`
- **get_all_devices()** (3 connections) — `src/interfaces/api/routers/admin.py`
- **get_duplicates()** (3 connections) — `src/interfaces/api/routers/admin.py`
- **reset_hero_password()** (3 connections) — `src/interfaces/api/routers/admin.py`
- **revoke_device()** (3 connections) — `src/interfaces/api/routers/admin.py`
- **BackgroundTasks** (3 connections)
- **delete** (2 connections)
- **patch** (1 connections)
- **Dispara la renovación manual/forzada de certificados SSL en segundo plano.** (1 connections) — `src/interfaces/api/routers/admin.py`

## Relationships

- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (14 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (9 shared connections)
- [Core: auth.py, SecurityShield](Core-_auth.py,_SecurityShield.md) (6 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (6 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (5 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (4 shared connections)
- [Services: SSLService, test_ssl_service.py](Services-_SSLService,_test_ssl_service.py.md) (4 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (4 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (3 shared connections)
- [Services: NexusService, .sync_catalog()](Services-_NexusService,_.sync_catalog.md) (2 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (2 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (2 shared connections)

## Source Files

- `src/interfaces/api/routers/admin.py`
- `src/interfaces/api/schemas.py`

## Audit Trail

- EXTRACTED: 81 (79%)
- INFERRED: 22 (21%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*