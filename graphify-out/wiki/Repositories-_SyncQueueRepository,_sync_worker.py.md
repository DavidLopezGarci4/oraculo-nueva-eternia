# Repositories: SyncQueueRepository, sync_worker.py

> 19 nodes

## Key Concepts

- **SyncQueueRepository** (13 connections) — `src/infrastructure/repositories/sync_queue.py`
- **sync_worker.py** (9 connections) — `src/application/jobs/sync_worker.py`
- **sync_queue.py** (8 connections) — `src/infrastructure/repositories/sync_queue.py`
- **SyncQueueModel** (6 connections) — `src/domain/models.py`
- **.process_queue()** (6 connections) — `src/application/jobs/sync_worker.py`
- **.push()** (5 connections) — `src/infrastructure/repositories/sync_queue.py`
- **SyncWorker** (4 connections) — `src/application/jobs/sync_worker.py`
- **.get_pending()** (3 connections) — `src/infrastructure/repositories/sync_queue.py`
- **.mark_failed()** (3 connections) — `src/infrastructure/repositories/sync_queue.py`
- **.mark_synced()** (3 connections) — `src/infrastructure/repositories/sync_queue.py`
- **.__init__()** (2 connections) — `src/infrastructure/repositories/sync_queue.py`
- **.__init__()** (1 connections) — `src/application/jobs/sync_worker.py`
- **Session** (1 connections)
- **Procesa un lote de la cola de sincronización.** (1 connections) — `src/application/jobs/sync_worker.py`
- **Cola de Sincronización Transaccional (Fase 3). Almacena las acciones pendientes…** (1 connections) — `src/domain/models.py`
- **Añade una acción a la cola local.** (1 connections) — `src/infrastructure/repositories/sync_queue.py`
- **Obtiene acciones pendientes para el worker.** (1 connections) — `src/infrastructure/repositories/sync_queue.py`
- **Marca un item como sincronizado exitosamente.** (1 connections) — `src/infrastructure/repositories/sync_queue.py`
- **Registra un fallo en la sincronización.** (1 connections) — `src/infrastructure/repositories/sync_queue.py`

## Relationships

- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (8 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (6 shared connections)
- [Scripts: ScraperStatusModel, ScraperExecutionLogModel](Scripts-_ScraperStatusModel,_ScraperExecutionLogModel.md) (1 shared connections)
- [Scripts: httpx, check_scraper_tokens.py](Scripts-_httpx,_check_scraper_tokens.py.md) (1 shared connections)
- [Collectors: personal_vintage_collection.py, time](Collectors-_personal_vintage_collection.py,_time.md) (1 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (1 shared connections)

## Source Files

- `src/application/jobs/sync_worker.py`
- `src/domain/models.py`
- `src/infrastructure/repositories/sync_queue.py`

## Audit Trail

- EXTRACTED: 36 (82%)
- INFERRED: 8 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*