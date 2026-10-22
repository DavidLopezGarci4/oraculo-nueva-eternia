# Routers: wallapop_jobs.py, WallapopJobModel

> 15 nodes

## Key Concepts

- **wallapop_jobs.py** (22 connections) — `src/interfaces/api/routers/wallapop_jobs.py`
- **WallapopJobModel** (13 connections) — `src/domain/models.py`
- **submit_wallapop_job_results()** (6 connections) — `src/interfaces/api/routers/wallapop_jobs.py`
- **create_wallapop_job()** (5 connections) — `src/interfaces/api/routers/wallapop_jobs.py`
- **WallapopJobResultsRequest** (4 connections) — `src/interfaces/api/schemas.py`
- **claim_pending_wallapop_job()** (4 connections) — `src/interfaces/api/routers/wallapop_jobs.py`
- **list_wallapop_jobs()** (4 connections) — `src/interfaces/api/routers/wallapop_jobs.py`
- **get** (2 connections)
- **post** (2 connections)
- **Nexus Local Bridge (Fase 2): cola de trabajos para que un worker ejecutado en…** (1 connections) — `src/domain/models.py`
- **Nexus Local Bridge (Fase 2 del plan…** (1 connections) — `src/interfaces/api/routers/wallapop_jobs.py`
- **Lista los trabajos más recientes del Nexus Local Bridge, para la UI de…** (1 connections) — `src/interfaces/api/routers/wallapop_jobs.py`
- **Encola un nuevo trabajo de búsqueda para el Nexus Local Bridge (Admin Only).** (1 connections) — `src/interfaces/api/routers/wallapop_jobs.py`
- **Reclama (y marca como 'running') el trabajo pendiente más antiguo, para que un…** (1 connections) — `src/interfaces/api/routers/wallapop_jobs.py`
- **Recibe los resultados de un worker local y los enruta al Purgatorio (Admin…** (1 connections) — `src/interfaces/api/routers/wallapop_jobs.py`

## Relationships

- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (8 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (4 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (4 shared connections)
- [Services: TelegramListener, .process_message()](Services-_TelegramListener,_.process_message.md) (2 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (2 shared connections)
- [Scrapers: ScrapingPipeline, test_scraper_interface.py](Scrapers-_ScrapingPipeline,_test_scraper_interface.py.md) (2 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (1 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (1 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (1 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (1 shared connections)

## Source Files

- `src/domain/models.py`
- `src/interfaces/api/routers/wallapop_jobs.py`
- `src/interfaces/api/schemas.py`

## Audit Trail

- EXTRACTED: 39 (83%)
- INFERRED: 8 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*