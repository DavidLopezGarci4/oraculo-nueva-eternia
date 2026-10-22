# Services: OracleAssistantAI, ._execute_tool()

> 21 nodes

## Key Concepts

- **OracleAssistantAI** (19 connections) — `src/application/services/telegram_oracle_ai.py`
- **._execute_tool()** (8 connections) — `src/application/services/telegram_oracle_ai.py`
- **.process_user_query()** (7 connections) — `src/application/services/telegram_oracle_ai.py`
- **test_telegram_oracle_ai.py** (7 connections) — `tests/unit/test_telegram_oracle_ai.py`
- **._process_with_local_brain()** (6 connections) — `src/application/services/telegram_oracle_ai.py`
- **test_telegram_oracle_ai_collection_query()** (5 connections) — `tests/unit/test_telegram_oracle_ai.py`
- **test_telegram_oracle_ai_deals_query()** (5 connections) — `tests/unit/test_telegram_oracle_ai.py`
- **Any** (5 connections)
- **._query_gemini_flash()** (4 connections) — `src/application/services/telegram_oracle_ai.py`
- **._tool_collection_summary()** (4 connections) — `src/application/services/telegram_oracle_ai.py`
- **._tool_figure_price()** (4 connections) — `src/application/services/telegram_oracle_ai.py`
- **._tool_top_opportunities()** (4 connections) — `src/application/services/telegram_oracle_ai.py`
- **._tool_missing_wishlist()** (3 connections) — `src/application/services/telegram_oracle_ai.py`
- **asyncio** (3 connections)
- **Ejecuta de forma segura funciones de solo lectura.** (1 connections) — `src/application/services/telegram_oracle_ai.py`
- **Motor semántico de reserva basado en patrones de lenguaje natural.** (1 connections) — `src/application/services/telegram_oracle_ai.py`
- **Asistente Conversacional Inteligente para Telegram ("El Ojo del Oráculo").…** (1 connections) — `src/application/services/telegram_oracle_ai.py`
- **Procesa una consulta en lenguaje natural y devuelve la respuesta formateada…** (1 connections) — `src/application/services/telegram_oracle_ai.py`
- **Consulta a Gemini Flash mediante Function Calling estructurado.** (1 connections) — `src/application/services/telegram_oracle_ai.py`
- **Prueba la respuesta semántica local sobre chollos y ofertas.** (1 connections) — `tests/unit/test_telegram_oracle_ai.py`
- **Prueba la respuesta semántica local sobre valor de la colección.** (1 connections) — `tests/unit/test_telegram_oracle_ai.py`

## Relationships

- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (2 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (2 shared connections)
- [Services: TelegramListener, .process_message()](Services-_TelegramListener,_.process_message.md) (2 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (1 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (1 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (1 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (1 shared connections)
- [Tests: conftest.py, unittest_mock](Tests-_conftest.py,_unittest_mock.md) (1 shared connections)

## Source Files

- `src/application/services/telegram_oracle_ai.py`
- `tests/unit/test_telegram_oracle_ai.py`

## Audit Trail

- EXTRACTED: 44 (86%)
- INFERRED: 7 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*