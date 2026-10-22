# Scrapers: search_wallapop_section(), test_wallapop_section_api.py

> 24 nodes

## Key Concepts

- **search_wallapop_section()** (16 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **test_wallapop_section_api.py** (16 connections) — `tests/unit/test_wallapop_section_api.py`
- **extract_image_url()** (8 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **parse_section_items()** (8 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **SectionSearchResult** (6 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **build_section_params()** (6 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **build_section_headers()** (5 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **test_search_wallapop_section_success()** (4 connections) — `tests/unit/test_wallapop_section_api.py`
- **test_search_wallapop_section_blocked()** (3 connections) — `tests/unit/test_wallapop_section_api.py`
- **Any** (3 connections)
- **test_build_section_headers()** (2 connections) — `tests/unit/test_wallapop_section_api.py`
- **test_build_section_params()** (2 connections) — `tests/unit/test_wallapop_section_api.py`
- **test_extract_image_url()** (2 connections) — `tests/unit/test_wallapop_section_api.py`
- **test_parse_section_items()** (2 connections) — `tests/unit/test_wallapop_section_api.py`
- **asyncio** (2 connections)
- **_log()** (1 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **AsyncSession** (1 connections)
- **Convierte la lista de items JSON de Wallapop section en instancias de…** (1 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **Ejecuta una petición orgánica contra /api/v3/search/section de Wallapop.…** (1 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **Resultado de búsqueda orgánica en Wallapop.** (1 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **Genera los parámetros para búsqueda inicial o paginación por token.** (1 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **Cabeceras requeridas para evadir bloqueos de la web de Wallapop.** (1 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **Extracción robusta de imagen. Para search/section (PokeCardTrack): prioriza…** (1 connections) — `src/infrastructure/scrapers/wallapop_section_api.py`
- **Tests unitarios (offline) para el motor orgánico de búsqueda de Wallapop…** (1 connections) — `tests/unit/test_wallapop_section_api.py`

## Relationships

- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (8 shared connections)
- [Scrapers: wallapop_scraper.py, WallapopScraper](Scrapers-_wallapop_scraper.py,_WallapopScraper.md) (4 shared connections)
- [Scrapers: ScrapedOffer, ._log()](Scrapers-_ScrapedOffer,_._log.md) (2 shared connections)
- [Unit: test_wallapop_signed_api.py, WallapopSigner](Unit-_test_wallapop_signed_api.py,_WallapopSigner.md) (1 shared connections)
- [Scrapers: WallapopManualScraper, nexus_local_worker.py](Scrapers-_WallapopManualScraper,_nexus_local_worker.py.md) (1 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (1 shared connections)
- [Tests: conftest.py, unittest_mock](Tests-_conftest.py,_unittest_mock.md) (1 shared connections)

## Source Files

- `src/infrastructure/scrapers/wallapop_section_api.py`
- `tests/unit/test_wallapop_section_api.py`

## Audit Trail

- EXTRACTED: 54 (96%)
- INFERRED: 2 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*