# Core: WeightEngine, ._compute()

> 17 nodes

## Key Concepts

- **WeightEngine** (13 connections) — `src/core/weight_engine.py`
- **._compute()** (5 connections) — `src/core/weight_engine.py`
- **.refresh()** (4 connections) — `src/core/weight_engine.py`
- **.refresh_from_products()** (4 connections) — `src/core/weight_engine.py`
- **._catalog_signature()** (3 connections) — `src/core/weight_engine.py`
- **.normalize()** (3 connections) — `src/core/weight_engine.py`
- **.get_weight()** (2 connections) — `src/core/weight_engine.py`
- **.__init__()** (2 connections) — `src/core/weight_engine.py`
- **.is_identity()** (2 connections) — `src/core/weight_engine.py`
- **.snapshot()** (2 connections) — `src/core/weight_engine.py`
- **.is_known()** (1 connections) — `src/core/weight_engine.py`
- **Devuelve el peso de un token. Si es conocido, se usa su IDF [1.0, 10.0]. Si es…** (1 connections) — `src/core/weight_engine.py`
- **(pesos, tokens_de_nombres) actuales. Los dicts se sustituyen atómicamente al…** (1 connections) — `src/core/weight_engine.py`
- **Determina si un token es una Identidad Crítica (peso > 5.0).** (1 connections) — `src/core/weight_engine.py`
- **Motor Dinámico de Pesos basado en IDF (Inverse Document Frequency). Analiza la…** (1 connections) — `src/core/weight_engine.py`
- **Recalcula los pesos analizando todos los productos de la DB configurada…** (1 connections) — `src/core/weight_engine.py`
- **Recalcula los pesos con el catálogo real que usa la petición (p.ej. Supabase).…** (1 connections) — `src/core/weight_engine.py`

## Relationships

- [Scripts: models.py, os](Scripts-_models.py,_os.md) (1 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (1 shared connections)
- [Core: tokenize(), text_normalization.py](Core-_tokenize,_text_normalization.py.md) (1 shared connections)

## Source Files

- `src/core/weight_engine.py`

## Audit Trail

- EXTRACTED: 24 (96%)
- INFERRED: 1 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*