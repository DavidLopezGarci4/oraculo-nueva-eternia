# Services: .get_market_summary(), .calculate_ideal_bid()

> 7 nodes

## Key Concepts

- **.get_market_summary()** (7 connections) — `src/application/services/market_intelligence.py`
- **.calculate_ideal_bid()** (4 connections) — `src/application/services/market_intelligence.py`
- **.get_monthly_price_evolution()** (4 connections) — `src/application/services/market_intelligence.py`
- **Any** (3 connections)
- **Resumen ejecutivo para el dashboard de inteligencia.** (1 connections) — `src/application/services/market_intelligence.py`
- **Calcula la evolución mensual del precio medio para un producto, segregando por…** (1 connections) — `src/application/services/market_intelligence.py`
- **Calcula el precio idóneo para pujar basándose en el percentil 25 de los items…** (1 connections) — `src/application/services/market_intelligence.py`

## Relationships

- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (5 shared connections)

## Source Files

- `src/application/services/market_intelligence.py`

## Audit Trail

- EXTRACTED: 11 (85%)
- INFERRED: 2 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*