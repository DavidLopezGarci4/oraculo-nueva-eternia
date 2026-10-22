# Unit: compute_suggestions(), test_api_link_memory.py

> 19 nodes

## Key Concepts

- **compute_suggestions()** (19 connections) — `src/interfaces/api/routers/purgatory.py`
- **test_api_link_memory.py** (18 connections) — `tests/unit/test_api_link_memory.py`
- **parse_history_rows()** (13 connections) — `src/core/link_memory.py`
- **TestLinkMemory** (8 connections) — `tests/unit/test_api_link_memory.py`
- **_row()** (8 connections) — `tests/unit/test_api_link_memory.py`
- **.test_learned_boost_reorders_close_candidates()** (6 connections) — `tests/unit/test_api_link_memory.py`
- **.test_learned_product_missing_from_candidates_is_added()** (6 connections) — `tests/unit/test_api_link_memory.py`
- **.test_learned_sculpt_is_flagged_but_never_preselected_over_exact_base()** (6 connections) — `tests/unit/test_api_link_memory.py`
- **_suggestion_sort_key()** (5 connections) — `src/interfaces/api/routers/purgatory.py`
- **.test_boost_is_capped_and_never_lowers_scores()** (5 connections) — `tests/unit/test_api_link_memory.py`
- **.test_similar_title_hits_and_different_title_does_not()** (4 connections) — `tests/unit/test_api_link_memory.py`
- **_item()** (3 connections) — `tests/unit/test_api_link_memory.py`
- **.test_parse_ignores_corrupt_and_empty_rows()** (3 connections) — `tests/unit/test_api_link_memory.py`
- **_serialize_suggestion()** (2 connections) — `src/interfaces/api/routers/purgatory.py`
- **.tearDownClass()** (1 connections) — `tests/unit/test_api_link_memory.py`
- **rows: iterable de (details_json, timestamp). Ignora filas corruptas o sin…** (1 connections) — `src/core/link_memory.py`
- **Calcula las predicciones de un anuncio del Purgatorio (ordenadas,…** (1 connections) — `src/interfaces/api/routers/purgatory.py`
- **Desempate determinista: puntuación, modernas primero, línea Origins principal,…** (1 connections) — `src/interfaces/api/routers/purgatory.py`
- **Tests de la memoria de vinculaciones manuales (reutiliza OfferHistoryModel, sin…** (1 connections) — `tests/unit/test_api_link_memory.py`

## Relationships

- [Core: link_memory.py, find_learned_hits()](Core-_link_memory.py,_find_learned_hits.md) (13 shared connections)
- [Unit: test_api_purgatory_scoring.py, build_suggestion_context()](Unit-_test_api_purgatory_scoring.py,_build_suggestion_context.md) (9 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (8 shared connections)
- [Core: tokenize(), text_normalization.py](Core-_tokenize,_text_normalization.py.md) (3 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (2 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (2 shared connections)
- [Unit: TestVintageSculptCompanions, ._sugs()](Unit-_TestVintageSculptCompanions,_._sugs.md) (1 shared connections)
- [Unit: TestPurgatoryScoring, ._top()](Unit-_TestPurgatoryScoring,_._top.md) (1 shared connections)

## Source Files

- `src/core/link_memory.py`
- `src/interfaces/api/routers/purgatory.py`
- `tests/unit/test_api_link_memory.py`

## Audit Trail

- EXTRACTED: 73 (97%)
- INFERRED: 2 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*