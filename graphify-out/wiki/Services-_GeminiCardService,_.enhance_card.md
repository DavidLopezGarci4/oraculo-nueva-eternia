# Services: GeminiCardService, .enhance_card()

> 25 nodes

## Key Concepts

- **GeminiCardService** (14 connections) — `src/application/services/gemini_card_service.py`
- **.enhance_card()** (10 connections) — `src/application/services/gemini_card_service.py`
- **test_gemini_card_service.py** (8 connections) — `tests/unit/test_gemini_card_service.py`
- **._generate_ai_art()** (6 connections) — `src/application/services/gemini_card_service.py`
- **enhance_card_with_ai()** (6 connections) — `src/interfaces/api/routers/cards.py`
- **._generate_lore_and_stats()** (5 connections) — `src/application/services/gemini_card_service.py`
- **test_enhance_card_alcala_texeira()** (5 connections) — `tests/unit/test_gemini_card_service.py`
- **test_enhance_card_legacy_aliases()** (5 connections) — `tests/unit/test_gemini_card_service.py`
- **test_enhance_card_obrero_norem()** (5 connections) — `tests/unit/test_gemini_card_service.py`
- **test_enhance_card_with_mocked_multimodal_gemini()** (5 connections) — `tests/unit/test_gemini_card_service.py`
- **asyncio** (4 connections)
- **._resolve_image_bytes()** (3 connections) — `src/application/services/gemini_card_service.py`
- **._resolve_style_key()** (3 connections) — `src/application/services/gemini_card_service.py`
- **Any** (2 connections)
- **post** (1 connections)
- **Ejecuta la transmutación mágica del cromo mediante Gemini multimodal (Flash…** (1 connections) — `src/application/services/gemini_card_service.py`
- **Servicio de Transformación Mágica de Cromos Digitales mediante la API…** (1 connections) — `src/application/services/gemini_card_service.py`
- **Resuelve la imagen de entrada a (mime_type, base64_data).** (1 connections) — `src/application/services/gemini_card_service.py`
- **Invoca la API multimodal de Gemini (gemini-2.5-flash-image / nano-banana) para…** (1 connections) — `src/application/services/gemini_card_service.py`
- **Genera el trasfondo canónico épico y estadísticas RPG enriquecidas mediante la…** (1 connections) — `src/application/services/gemini_card_service.py`
- **Transforma un cromo digital usando la API de Gemini / Imagen 3 para arte retro…** (1 connections) — `src/interfaces/api/routers/cards.py`
- **Verifica el estilo mini-cómic vintage de Alfredo Alcala y Mark Texeira.** (1 connections) — `tests/unit/test_gemini_card_service.py`
- **Verifica que los estilos antiguos se mapeen correctamente a los estilos de…** (1 connections) — `tests/unit/test_gemini_card_service.py`
- **Verifica la integración con mock de la respuesta multimodal de Gemini Flash…** (1 connections) — `tests/unit/test_gemini_card_service.py`
- **Verifica que la generación de óleo box-art estilo Rudy Obrero y Earl Norem…** (1 connections) — `tests/unit/test_gemini_card_service.py`

## Relationships

- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (3 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (2 shared connections)
- [Api: api/schemas.py, BaseModel](Api-_api-schemas.py,_BaseModel.md) (1 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (1 shared connections)
- [Tests: conftest.py, unittest_mock](Tests-_conftest.py,_unittest_mock.md) (1 shared connections)

## Source Files

- `src/application/services/gemini_card_service.py`
- `src/interfaces/api/routers/cards.py`
- `tests/unit/test_gemini_card_service.py`

## Audit Trail

- EXTRACTED: 44 (88%)
- INFERRED: 6 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*