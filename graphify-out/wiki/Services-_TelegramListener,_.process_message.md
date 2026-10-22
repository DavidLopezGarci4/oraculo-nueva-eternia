# Services: TelegramListener, .process_message()

> 25 nodes

## Key Concepts

- **TelegramListener** (43 connections) — `src/infrastructure/services/telegram_listener.py`
- **.process_message()** (24 connections) — `src/infrastructure/services/telegram_listener.py`
- **.is_sovereign_admin()** (6 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_harvest_lore()** (5 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_update_image()** (4 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_approve_device()** (3 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_caza()** (3 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_deny_device()** (3 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_devices()** (3 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_nexus()** (3 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_renew_ssl()** (3 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_run()** (3 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_buscar()** (2 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_centinela()** (2 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_help()** (2 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_purgatorio()** (2 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_register()** (2 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_status()** (2 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_tokens()** (2 connections) — `src/infrastructure/services/telegram_listener.py`
- **.__init__()** (1 connections) — `src/infrastructure/services/telegram_listener.py`
- **.stop_polling()** (1 connections) — `src/infrastructure/services/telegram_listener.py`
- **Escucha y procesa comandos de Telegram en segundo plano mediante Long Polling.** (1 connections) — `src/infrastructure/services/telegram_listener.py`
- **Determina si el chat_id corresponde única y exclusivamente al Gran Arquitecto /…** (1 connections) — `src/infrastructure/services/telegram_listener.py`
- **Descarga la imagen actualizada de una figura desde ActionFigure411.** (1 connections) — `src/infrastructure/services/telegram_listener.py`
- **Cosecha lore desde Wiki Fandom para una figura o personaje.** (1 connections) — `src/infrastructure/services/telegram_listener.py`

## Relationships

- [Services: .process_callback_query(), .get_user_status()](Services-_.process_callback_query,_.get_user_status.md) (11 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (3 shared connections)
- [Services: WallapopBridge, .get_item_details()](Services-_WallapopBridge,_.get_item_details.md) (3 shared connections)
- [Routers: lore.py, LoreHarvesterService](Routers-_lore.py,_LoreHarvesterService.md) (3 shared connections)
- [Routers: stop_scrapers(), import_wallapop_manual_html()](Routers-_stop_scrapers,_import_wallapop_manual_html.md) (2 shared connections)
- [Services: SSLService, test_ssl_service.py](Services-_SSLService,_test_ssl_service.py.md) (2 shared connections)
- [Services: OracleAssistantAI, ._execute_tool()](Services-_OracleAssistantAI,_._execute_tool.md) (2 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (2 shared connections)
- [Routers: wallapop_jobs.py, WallapopJobModel](Routers-_wallapop_jobs.py,_WallapopJobModel.md) (2 shared connections)
- [Services: VintedHunterService, .run_hunt()](Services-_VintedHunterService,_.run_hunt.md) (2 shared connections)
- [Services: NexusService, .sync_catalog()](Services-_NexusService,_.sync_catalog.md) (2 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (1 shared connections)

## Source Files

- `src/infrastructure/services/telegram_listener.py`

## Audit Trail

- EXTRACTED: 66 (82%)
- INFERRED: 14 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*