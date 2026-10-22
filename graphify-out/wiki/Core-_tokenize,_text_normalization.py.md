# Core: tokenize(), text_normalization.py

> 14 nodes

## Key Concepts

- **tokenize()** (20 connections) — `src/core/text_normalization.py`
- **text_normalization.py** (12 connections) — `src/core/text_normalization.py`
- **purgatory_companions.py** (7 connections) — `src/core/purgatory_companions.py`
- **inject_vintage_sculpt_companions()** (6 connections) — `src/core/purgatory_companions.py`
- **build_companion_lookup()** (5 connections) — `src/core/purgatory_companions.py`
- **_norm_name()** (3 connections) — `src/core/purgatory_companions.py`
- **_ascii_lower()** (3 connections) — `src/core/text_normalization.py`
- **unicodedata** (3 connections)
- **.test_the_original_is_not_collapsed_into_base_name()** (2 connections) — `tests/unit/test_api_purgatory_scoring.py`
- **Predicciones acompañantes del Purgatorio. Las figuras Origins "He-Man (Vintage…** (1 connections) — `src/core/purgatory_companions.py`
- **Mapa nombre exacto (minúsculas) -> producto NO vintage, solo para los…** (1 connections) — `src/core/purgatory_companions.py`
- **Inserta (o reubica) el acompañante Vintage Sculpt justo detrás de cada He-Man /…** (1 connections) — `src/core/purgatory_companions.py`
- **Normalización de texto compartida por el motor de matching (brain_engine), el…** (1 connections) — `src/core/text_normalization.py`
- **Tokens significativos normalizados (compuestos unidos, sinónimos, sin…** (1 connections) — `src/core/text_normalization.py`

## Relationships

- [Core: brain_engine.py, .calculate_match()](Core-_brain_engine.py,_.calculate_match.md) (5 shared connections)
- [Unit: test_api_purgatory_scoring.py, build_suggestion_context()](Unit-_test_api_purgatory_scoring.py,_build_suggestion_context.md) (4 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (4 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (3 shared connections)
- [Unit: compute_suggestions(), test_api_link_memory.py](Unit-_compute_suggestions,_test_api_link_memory.py.md) (3 shared connections)
- [Core: link_memory.py, find_learned_hits()](Core-_link_memory.py,_find_learned_hits.md) (3 shared connections)
- [Unit: TestPurgatoryScoring, ._top()](Unit-_TestPurgatoryScoring,_._top.md) (2 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (2 shared connections)
- [Core: WeightEngine, ._compute()](Core-_WeightEngine,_._compute.md) (1 shared connections)
- [Services: VintedHunterService, .run_hunt()](Services-_VintedHunterService,_.run_hunt.md) (1 shared connections)

## Source Files

- `src/core/purgatory_companions.py`
- `src/core/text_normalization.py`
- `tests/unit/test_api_purgatory_scoring.py`

## Audit Trail

- EXTRACTED: 47 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*