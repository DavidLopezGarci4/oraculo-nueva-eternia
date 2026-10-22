# Unit: check_is_vintage(), vintage_utils.py

> 9 nodes

## Key Concepts

- **check_is_vintage()** (15 connections) — `src/core/vintage_utils.py`
- **vintage_utils.py** (7 connections) — `src/core/vintage_utils.py`
- **TestCheckIsVintageOriginsSculpt** (5 connections) — `tests/unit/test_api_vintage_sculpt_detection.py`
- **test_api_vintage_sculpt_detection.py** (4 connections) — `tests/unit/test_api_vintage_sculpt_detection.py`
- **.test_empty_and_modern_titles()** (2 connections) — `tests/unit/test_api_vintage_sculpt_detection.py`
- **.test_real_vintage_titles_are_still_vintage()** (2 connections) — `tests/unit/test_api_vintage_sculpt_detection.py`
- **.test_sculpt_phrase_does_not_hide_other_vintage_signals()** (2 connections) — `tests/unit/test_api_vintage_sculpt_detection.py`
- **.test_vintage_sculpt_origins_titles_are_not_vintage()** (2 connections) — `tests/unit/test_api_vintage_sculpt_detection.py`
- **Checks if the given text indicates a vintage item. Returns True if the text…** (1 connections) — `src/core/vintage_utils.py`

## Relationships

- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (5 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (2 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (2 shared connections)
- [Scrapers: SmythsToysScraper, ._parse_html()](Scrapers-_SmythsToysScraper,_._parse_html.md) (2 shared connections)
- [Unit: validate_motu_relevance(), test_api_motu_relevance.py](Unit-_validate_motu_relevance,_test_api_motu_relevance.py.md) (2 shared connections)
- [Unit: test_api_purgatory_scoring.py, build_suggestion_context()](Unit-_test_api_purgatory_scoring.py,_build_suggestion_context.md) (1 shared connections)

## Source Files

- `src/core/vintage_utils.py`
- `tests/unit/test_api_vintage_sculpt_detection.py`

## Audit Trail

- EXTRACTED: 24 (89%)
- INFERRED: 3 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*