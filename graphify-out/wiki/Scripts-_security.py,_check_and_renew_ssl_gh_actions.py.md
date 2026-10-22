# Scripts: security.py, check_and_renew_ssl_gh_actions.py

> 17 nodes

## Key Concepts

- **security.py** (18 connections) — `src/core/security.py`
- **check_and_renew_ssl_gh_actions.py** (17 connections) — `scripts/check_and_renew_ssl_gh_actions.py`
- **ssl_service.py** (16 connections) — `src/application/services/ssl_service.py`
- **subprocess** (14 connections)
- **agent.py** (12 connections) — `.agents/skills/implementing-secrets-scanning-in-ci-cd/scripts/agent.py`
- **main()** (8 connections) — `.agents/skills/implementing-secrets-scanning-in-ci-cd/scripts/agent.py`
- **ensure_chrome_debug_running()** (7 connections) — `scripts/scrape_multi_via_cdp.py`
- **run_gitleaks()** (6 connections) — `.agents/skills/implementing-secrets-scanning-in-ci-cd/scripts/agent.py`
- **socket** (6 connections)
- **tempfile** (6 connections)
- **run_trufflehog()** (4 connections) — `.agents/skills/implementing-secrets-scanning-in-ci-cd/scripts/agent.py`
- **is_chrome_debug_port_open()** (3 connections) — `scripts/scrape_multi_via_cdp.py`
- **evaluate_gate()** (2 connections) — `.agents/skills/implementing-secrets-scanning-in-ci-cd/scripts/agent.py`
- **find_chrome_executable()** (2 connections) — `scripts/scrape_multi_via_cdp.py`
- **ssl** (2 connections)
- **Secrets scanning CI/CD gate using gitleaks and trufflehog.** (1 connections) — `.agents/skills/implementing-secrets-scanning-in-ci-cd/scripts/agent.py`
- **Script de comprobación y renovación automática de certificados SSL para GitHub…** (1 connections) — `scripts/check_and_renew_ssl_gh_actions.py`

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (17 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (13 shared connections)
- [Core: auth.py, SecurityShield](Core-_auth.py,_SecurityShield.md) (5 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (5 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (4 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (3 shared connections)
- [Collectors: personal_vintage_collection.py, time](Collectors-_personal_vintage_collection.py,_time.md) (3 shared connections)
- [Services: SSLService, test_ssl_service.py](Services-_SSLService,_test_ssl_service.py.md) (3 shared connections)
- [Scripts: httpx, check_scraper_tokens.py](Scripts-_httpx,_check_scraper_tokens.py.md) (3 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (2 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (2 shared connections)
- [Experimental: render_burn_vfx.py, render_grayskull_vfx.py](Experimental-_render_burn_vfx.py,_render_grayskull_vfx.py.md) (2 shared connections)

## Source Files

- `.agents/skills/implementing-secrets-scanning-in-ci-cd/scripts/agent.py`
- `scripts/check_and_renew_ssl_gh_actions.py`
- `scripts/scrape_multi_via_cdp.py`
- `src/application/services/ssl_service.py`
- `src/core/security.py`

## Audit Trail

- EXTRACTED: 97 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*