# Services: GitHubQuotaService, github_quota_service.py

> 24 nodes

## Key Concepts

- **GitHubQuotaService** (15 connections) — `src/application/services/github_quota_service.py`
- **github_quota_service.py** (13 connections) — `src/application/services/github_quota_service.py`
- **test_github_quota_service.py** (11 connections) — `tests/unit/test_github_quota_service.py`
- **.get_quota_status()** (8 connections) — `src/application/services/github_quota_service.py`
- **._fetch_db_logs_this_month()** (5 connections) — `src/application/services/github_quota_service.py`
- **._fetch_github_runs_this_month()** (5 connections) — `src/application/services/github_quota_service.py`
- **.generate_logs_csv()** (5 connections) — `src/application/services/github_quota_service.py`
- **export_execution_logs_csv()** (5 connections) — `src/interfaces/api/routers/scrapers.py`
- **get_github_quota_status()** (5 connections) — `src/interfaces/api/routers/scrapers.py`
- **test_quota_service_db_fallback()** (5 connections) — `tests/unit/test_github_quota_service.py`
- **test_generate_logs_csv()** (4 connections) — `tests/unit/test_github_quota_service.py`
- **test_quota_service_with_github_api()** (4 connections) — `tests/unit/test_github_quota_service.py`
- **Any** (3 connections)
- **datetime** (3 connections)
- **._render_csv()** (2 connections) — `src/application/services/github_quota_service.py`
- **asyncio** (2 connections)
- **Consulta la API de GitHub Actions para el repositorio y mes actual.** (1 connections) — `src/application/services/github_quota_service.py`
- **Servicio de Telemetría FinOps y Sincronización en Vivo con GitHub Actions.…** (1 connections) — `src/application/services/github_quota_service.py`
- **Consulta los registros de ScraperExecutionLogModel en base de datos como…** (1 connections) — `src/application/services/github_quota_service.py`
- **Genera el contenido en formato CSV de todo el historial de ejecuciones.** (1 connections) — `src/application/services/github_quota_service.py`
- **Obtiene el estado de la cuota mensual combinando GitHub API en vivo y base de…** (1 connections) — `src/application/services/github_quota_service.py`
- **Retorna el estado en vivo de la cuota mensual de GitHub Actions (2.000 min),…** (1 connections) — `src/interfaces/api/routers/scrapers.py`
- **Genera y descarga un archivo CSV con el historial de ejecuciones y minutos…** (1 connections) — `src/interfaces/api/routers/scrapers.py`
- **csv** (1 connections)

## Relationships

- [Scrapers: scrapers.py, run_scraper_task()](Scrapers-_scrapers.py,_run_scraper_task.md) (5 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (5 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (4 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (2 shared connections)
- [Tests: conftest.py, unittest_mock](Tests-_conftest.py,_unittest_mock.md) (2 shared connections)
- [Experimental: render_burn_vfx.py, render_grayskull_vfx.py](Experimental-_render_burn_vfx.py,_render_grayskull_vfx.py.md) (1 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (1 shared connections)
- [Scripts: httpx, check_scraper_tokens.py](Scripts-_httpx,_check_scraper_tokens.py.md) (1 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (1 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (1 shared connections)

## Source Files

- `src/application/services/github_quota_service.py`
- `src/interfaces/api/routers/scrapers.py`
- `tests/unit/test_github_quota_service.py`

## Audit Trail

- EXTRACTED: 56 (89%)
- INFERRED: 7 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*