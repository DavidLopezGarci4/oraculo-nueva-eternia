# Tests: conftest.py, unittest_mock

> 22 nodes

## Key Concepts

- **conftest.py** (23 connections) — `tests/conftest.py`
- **unittest_mock** (17 connections)
- **fixture** (7 connections)
- **client()** (5 connections) — `tests/conftest.py`
- **verify_logistics_api.py** (4 connections) — `scripts/verify_logistics_api.py`
- **admin_bearer()** (3 connections) — `tests/conftest.py`
- **admin_user()** (3 connections) — `tests/conftest.py`
- **authorized_device_headers()** (3 connections) — `tests/conftest.py`
- **bearer()** (3 connections) — `tests/conftest.py`
- **test_user()** (3 connections) — `tests/conftest.py`
- **viewer_token()** (3 connections) — `tests/conftest.py`
- **test_logistics_integration()** (2 connections) — `scripts/verify_logistics_api.py`
- **fastapi_testclient** (2 connections)
- **sqlalchemy_pool** (2 connections)
- **Test infrastructure for the Oráculo API. Uses an in-memory SQLite database…** (1 connections) — `tests/conftest.py`
- **Register a viewer user once and return its credentials.** (1 connections) — `tests/conftest.py`
- **JWT token for the viewer test user.** (1 connections) — `tests/conftest.py`
- **Authorization header with viewer JWT.** (1 connections) — `tests/conftest.py`
- **Create an admin-role user via the service-to-service admin endpoint.** (1 connections) — `tests/conftest.py`
- **Authorization header with an admin JWT (real login, not the API-key bypass).** (1 connections) — `tests/conftest.py`
- **Headers for a device that has gone through the REAL approval flow: 1. First…** (1 connections) — `tests/conftest.py`
- **FastAPI TestClient backed by an in-memory SQLite database. Patches are started…** (1 connections) — `tests/conftest.py`

## Relationships

- [Services: LogisticsService, LogisticRuleModel](Services-_LogisticsService,_LogisticRuleModel.md) (4 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (3 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (3 shared connections)
- [Services: VintedHunterService, .run_hunt()](Services-_VintedHunterService,_.run_hunt.md) (3 shared connections)
- [Scripts: seed_logistics(), seed_logistics.py](Scripts-_seed_logistics,_seed_logistics.py.md) (2 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (2 shared connections)
- [Services: GitHubQuotaService, github_quota_service.py](Services-_GitHubQuotaService,_github_quota_service.py.md) (2 shared connections)
- [Integration: test_api_image_cache.py, _fetch_and_cache_product_image()](Integration-_test_api_image_cache.py,__fetch_and_cache_product_image.md) (2 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (1 shared connections)
- [Integration: test_api_permissions.py, test_collection_non_admin_cannot_read_other_users()](Integration-_test_api_permissions.py,_test_collection_non_admin_cannot_read_other_users.md) (1 shared connections)
- [Integration: test_api_response_schemas.py, test_scrapers_status_logs_ip_logs_match_schema()](Integration-_test_api_response_schemas.py,_test_scrapers_status_logs_ip_logs_match_schema.md) (1 shared connections)
- [Integration: test_api_ssl.py, test_get_ssl_status_rejects_unauthenticated()](Integration-_test_api_ssl.py,_test_get_ssl_status_rejects_unauthenticated.md) (1 shared connections)

## Source Files

- `scripts/verify_logistics_api.py`
- `tests/conftest.py`

## Audit Trail

- EXTRACTED: 60 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*