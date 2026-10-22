# Core: auth.py, SecurityShield

> 51 nodes

## Key Concepts

- **auth.py** (35 connections) — `src/interfaces/api/routers/auth.py`
- **SecurityShield** (27 connections) — `src/core/security.py`
- **is_admin()** (13 connections) — `src/interfaces/api/deps.py`
- **login()** (9 connections) — `src/interfaces/api/routers/auth.py`
- **email_service.py** (9 connections) — `src/infrastructure/email_service.py`
- **.send_telegram_alert()** (8 connections) — `src/core/security.py`
- **forgot_password()** (8 connections) — `src/interfaces/api/routers/auth.py`
- **rate_limit.py** (8 connections) — `src/core/rate_limit.py`
- **register()** (7 connections) — `src/interfaces/api/routers/auth.py`
- **reset_password()** (7 connections) — `src/interfaces/api/routers/auth.py`
- **init_passwords.py** (7 connections) — `scripts/maintenance/init_passwords.py`
- **.check_access()** (6 connections) — `src/core/security.py`
- **.hash_password()** (6 connections) — `src/core/security.py`
- **require_admin()** (6 connections) — `src/interfaces/api/deps.py`
- **run_maintenance_task()** (6 connections) — `src/interfaces/api/routers/system.py`
- **EmailService** (4 connections) — `src/infrastructure/email_service.py`
- **LoginRequest** (4 connections) — `src/interfaces/api/schemas.py`
- **ResetPasswordRequest** (4 connections) — `src/interfaces/api/schemas.py`
- **init_user_passwords()** (4 connections) — `scripts/maintenance/init_passwords.py`
- **rate_limit()** (4 connections) — `src/core/rate_limit.py`
- **.authorize_device()** (4 connections) — `src/core/security.py`
- **create_access_token()** (4 connections) — `src/interfaces/api/deps.py`
- **get_users_minimal()** (4 connections) — `src/interfaces/api/routers/auth.py`
- **post** (4 connections)
- **.verify_password()** (3 connections) — `src/core/security.py`
- *... and 26 more nodes in this community*

## Relationships

- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (20 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (13 shared connections)
- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (12 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (8 shared connections)
- [Routers: admin.py, post](Routers-_admin.py,_post.md) (6 shared connections)
- [Scripts: security.py, check_and_renew_ssl_gh_actions.py](Scripts-_security.py,_check_and_renew_ssl_gh_actions.py.md) (5 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (5 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (3 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (2 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (2 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (2 shared connections)
- [Services: SSLService, test_ssl_service.py](Services-_SSLService,_test_ssl_service.py.md) (2 shared connections)

## Source Files

- `scripts/maintenance/init_passwords.py`
- `src/core/rate_limit.py`
- `src/core/security.py`
- `src/infrastructure/email_service.py`
- `src/interfaces/api/deps.py`
- `src/interfaces/api/routers/auth.py`
- `src/interfaces/api/routers/system.py`
- `src/interfaces/api/schemas.py`

## Audit Trail

- EXTRACTED: 129 (82%)
- INFERRED: 28 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*