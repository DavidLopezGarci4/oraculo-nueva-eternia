# Core: get_product_details(), search_product()

> 6 nodes

## Key Concepts

- **get_product_details()** (5 connections) — `src/core/mcp_server.py`
- **search_product()** (4 connections) — `src/core/mcp_server.py`
- **.get_by_name()** (3 connections) — `src/infrastructure/repositories/product.py`
- **tool** (2 connections)
- **Busca productos en la base de datos de Eternia por nombre. Retorna una lista de…** (1 connections) — `src/core/mcp_server.py`
- **Obtiene los detalles completos de un producto dado su nombre exacto.** (1 connections) — `src/core/mcp_server.py`

## Relationships

- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (3 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (2 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (1 shared connections)

## Source Files

- `src/core/mcp_server.py`
- `src/infrastructure/repositories/product.py`

## Audit Trail

- EXTRACTED: 8 (73%)
- INFERRED: 3 (27%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*