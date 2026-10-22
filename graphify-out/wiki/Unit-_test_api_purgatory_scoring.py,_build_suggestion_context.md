# Unit: test_api_purgatory_scoring.py, build_suggestion_context()

> 19 nodes

## Key Concepts

- **test_api_purgatory_scoring.py** (17 connections) — `tests/unit/test_api_purgatory_scoring.py`
- **build_suggestion_context()** (15 connections) — `src/interfaces/api/routers/purgatory.py`
- **test_api_purgatory_companions.py** (10 connections) — `tests/unit/test_api_purgatory_companions.py`
- **unittest** (9 connections)
- **_ean_key()** (7 connections) — `src/interfaces/api/routers/purgatory.py`
- **_build_product_index()** (5 connections) — `src/interfaces/api/routers/purgatory.py`
- **test_models.py** (3 connections) — `dev_tools/test_models.py`
- **types** (3 connections)
- **_item()** (2 connections) — `tests/unit/test_api_purgatory_companions.py`
- **.setUpClass()** (2 connections) — `tests/unit/test_api_purgatory_companions.py`
- **_item()** (2 connections) — `tests/unit/test_api_purgatory_scoring.py`
- **.setUpClass()** (2 connections) — `tests/unit/test_api_purgatory_scoring.py`
- **.test_ean_keys_ignore_formatting_and_leading_zeros()** (2 connections) — `tests/unit/test_api_purgatory_scoring.py`
- **_p()** (1 connections) — `tests/unit/test_api_purgatory_scoring.py`
- **Prepara índices y pesos IDF con el catálogo real de la petición (una vez por…** (1 connections) — `src/interfaces/api/routers/purgatory.py`
- **Builds two lookup structures from the product list (called once per request):…** (1 connections) — `src/interfaces/api/routers/purgatory.py`
- **Clave de EAN normalizada (solo dígitos, sin ceros a la izquierda).** (1 connections) — `src/interfaces/api/routers/purgatory.py`
- **Tests del acompaÃ±ante Vintage Sculpt (figuras Origins, NO vintage) en las…** (1 connections) — `tests/unit/test_api_purgatory_companions.py`
- **Tests de precisión del matching del Purgatorio con un catálogo ficticio…** (1 connections) — `tests/unit/test_api_purgatory_scoring.py`

## Relationships

- [Unit: compute_suggestions(), test_api_link_memory.py](Unit-_compute_suggestions,_test_api_link_memory.py.md) (9 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (6 shared connections)
- [Core: tokenize(), text_normalization.py](Core-_tokenize,_text_normalization.py.md) (4 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (4 shared connections)
- [Unit: TestVintageSculptCompanions, ._sugs()](Unit-_TestVintageSculptCompanions,_._sugs.md) (4 shared connections)
- [Unit: TestPurgatoryScoring, ._top()](Unit-_TestPurgatoryScoring,_._top.md) (4 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (4 shared connections)
- [Core: brain_engine.py, .calculate_match()](Core-_brain_engine.py,_.calculate_match.md) (2 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (1 shared connections)
- [Dev_tools: TestProductOffer, .test_display_price()](Dev_tools-_TestProductOffer,_.test_display_price.md) (1 shared connections)
- [Scrapers: ScrapingPipeline, test_scraper_interface.py](Scrapers-_ScrapingPipeline,_test_scraper_interface.py.md) (1 shared connections)
- [Unit: check_is_vintage(), vintage_utils.py](Unit-_check_is_vintage,_vintage_utils.py.md) (1 shared connections)

## Source Files

- `dev_tools/test_models.py`
- `src/interfaces/api/routers/purgatory.py`
- `tests/unit/test_api_purgatory_companions.py`
- `tests/unit/test_api_purgatory_scoring.py`

## Audit Trail

- EXTRACTED: 63 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*