# Routers: stop_scrapers(), import_wallapop_manual_html()

> 11 nodes

## Key Concepts

- **stop_scrapers()** (9 connections) — `src/interfaces/api/routers/scrapers.py`
- **import_wallapop_manual_html()** (8 connections) — `src/interfaces/api/routers/scrapers.py`
- **run_scrapers()** (8 connections) — `src/interfaces/api/routers/scrapers.py`
- **.cmd_stop()** (3 connections) — `src/infrastructure/services/telegram_listener.py`
- **post** (3 connections)
- **psutil** (2 connections)
- **BackgroundTasks** (1 connections)
- **UploadFile** (1 connections)
- **Inicia la recolección de reliquias en segundo plano (Admin Only)** (1 connections) — `src/interfaces/api/routers/scrapers.py`
- **Protocolo de Emergencia: Mata procesos de scrapers activos y resetea estados en…** (1 connections) — `src/interfaces/api/routers/scrapers.py`
- **Parsea el archivo local o subido data/wallapop_search.html e inserta los…** (1 connections) — `src/interfaces/api/routers/scrapers.py`

## Relationships

- [Scrapers: scrapers.py, run_scraper_task()](Scrapers-_scrapers.py,_run_scraper_task.md) (5 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (4 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (4 shared connections)
- [Services: TelegramListener, .process_message()](Services-_TelegramListener,_.process_message.md) (2 shared connections)
- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (1 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (1 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (1 shared connections)

## Source Files

- `src/infrastructure/services/telegram_listener.py`
- `src/interfaces/api/routers/scrapers.py`

## Audit Trail

- EXTRACTED: 18 (64%)
- INFERRED: 10 (36%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*