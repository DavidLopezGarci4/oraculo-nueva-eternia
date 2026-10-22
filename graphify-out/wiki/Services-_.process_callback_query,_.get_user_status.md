# Services: .process_callback_query(), .get_user_status()

> 10 nodes

## Key Concepts

- **.process_callback_query()** (11 connections) — `src/infrastructure/services/telegram_listener.py`
- **.get_user_status()** (5 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_alertas()** (4 connections) — `src/infrastructure/services/telegram_listener.py`
- **.cmd_ssl_status()** (4 connections) — `src/infrastructure/services/telegram_listener.py`
- **.start_polling()** (4 connections) — `src/infrastructure/services/telegram_listener.py`
- **.answer_callback_query()** (3 connections) — `src/infrastructure/services/telegram_listener.py`
- **Responde a un callback_query de Telegram para finalizar la animación de carga.** (1 connections) — `src/infrastructure/services/telegram_listener.py`
- **Procesa pulsaciones de botones Inline de Telegram.** (1 connections) — `src/infrastructure/services/telegram_listener.py`
- **Devuelve (is_admin, is_guardian, user_obj).** (1 connections) — `src/infrastructure/services/telegram_listener.py`
- **Inicia el bucle asíncrono de escucha en segundo plano.** (1 connections) — `src/infrastructure/services/telegram_listener.py`

## Relationships

- [Services: TelegramListener, .process_message()](Services-_TelegramListener,_.process_message.md) (11 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (4 shared connections)
- [Services: SSLService, test_ssl_service.py](Services-_SSLService,_test_ssl_service.py.md) (2 shared connections)

## Source Files

- `src/infrastructure/services/telegram_listener.py`

## Audit Trail

- EXTRACTED: 26 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*