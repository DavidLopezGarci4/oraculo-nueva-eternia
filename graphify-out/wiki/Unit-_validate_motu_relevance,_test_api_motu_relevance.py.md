# Unit: validate_motu_relevance(), test_api_motu_relevance.py

> 8 nodes

## Key Concepts

- **validate_motu_relevance()** (15 connections) — `src/core/vintage_utils.py`
- **test_api_motu_relevance.py** (8 connections) — `tests/unit/test_api_motu_relevance.py`
- **test_validate_motu_relevance_invalid_big_jim()** (2 connections) — `tests/unit/test_api_motu_relevance.py`
- **test_validate_motu_relevance_invalid_funko()** (2 connections) — `tests/unit/test_api_motu_relevance.py`
- **test_validate_motu_relevance_invalid_masterverse()** (2 connections) — `tests/unit/test_api_motu_relevance.py`
- **test_validate_motu_relevance_non_motu_vintage()** (2 connections) — `tests/unit/test_api_motu_relevance.py`
- **test_validate_motu_relevance_valid_cases()** (2 connections) — `tests/unit/test_api_motu_relevance.py`
- **Validates if a given text title is relevant to the Masters of the Universe…** (1 connections) — `src/core/vintage_utils.py`

## Relationships

- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (2 shared connections)
- [Unit: check_is_vintage(), vintage_utils.py](Unit-_check_is_vintage,_vintage_utils.py.md) (2 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (1 shared connections)
- [Services: WallapopBridge, .get_item_details()](Services-_WallapopBridge,_.get_item_details.md) (1 shared connections)
- [Scripts: database_cloud.py, loguru](Scripts-_database_cloud.py,_loguru.md) (1 shared connections)
- [Routers: UserModel, system.py](Routers-_UserModel,_system.py.md) (1 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (1 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (1 shared connections)

## Source Files

- `src/core/vintage_utils.py`
- `tests/unit/test_api_motu_relevance.py`

## Audit Trail

- EXTRACTED: 22 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*