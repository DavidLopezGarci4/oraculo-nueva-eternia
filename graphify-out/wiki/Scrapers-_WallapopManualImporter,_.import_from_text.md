# Scrapers: WallapopManualImporter, .import_from_text()

> 14 nodes

## Key Concepts

- **WallapopManualImporter** (10 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **.import_from_text()** (6 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **.import_from_file()** (5 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **._save_to_purgatory()** (5 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **.parse_simple_format()** (4 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **.parse_url_list()** (4 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **run_import()** (3 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **.__init__()** (1 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **Importa datos desde texto directo (clipboard, etc).** (1 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **Guarda las ofertas en la tabla de Purgatorio para revisión manual.** (1 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **Importador manual para datos de Wallapop. Soporta múltiples formatos de entrada.** (1 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **Parsea texto en formato simple: Nombre del producto | Precio | URL Ejemplo: He-…** (1 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **Extrae y normaliza URLs de Wallapop de un texto (eliminando parámetros de…** (1 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`
- **Importa datos desde un archivo .txt o .csv.** (1 connections) — `src/infrastructure/scrapers/wallapop_manual_importer.py`

## Relationships

- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (2 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (2 shared connections)

## Source Files

- `src/infrastructure/scrapers/wallapop_manual_importer.py`

## Audit Trail

- EXTRACTED: 22 (92%)
- INFERRED: 2 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*