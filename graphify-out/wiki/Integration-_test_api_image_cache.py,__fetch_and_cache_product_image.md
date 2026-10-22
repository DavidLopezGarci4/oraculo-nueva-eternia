# Integration: test_api_image_cache.py, _fetch_and_cache_product_image()

> 14 nodes

## Key Concepts

- **test_api_image_cache.py** (18 connections) — `tests/integration/test_api_image_cache.py`
- **_fetch_and_cache_product_image()** (11 connections) — `src/interfaces/api/main.py`
- **_make_test_session()** (6 connections) — `tests/integration/test_api_image_cache.py`
- **test_downloads_converts_and_caches_as_webp()** (6 connections) — `tests/integration/test_api_image_cache.py`
- **test_returns_none_when_product_has_no_image_url()** (5 connections) — `tests/integration/test_api_image_cache.py`
- **_FakeResponse** (4 connections) — `tests/integration/test_api_image_cache.py`
- **_fake_source_image_bytes()** (4 connections) — `tests/integration/test_api_image_cache.py`
- **test_returns_none_and_does_not_crash_on_download_failure()** (4 connections) — `tests/integration/test_api_image_cache.py`
- **test_returns_none_for_nonexistent_product()** (4 connections) — `tests/integration/test_api_image_cache.py`
- **.__init__()** (1 connections) — `tests/integration/test_api_image_cache.py`
- **.raise_for_status()** (1 connections) — `tests/integration/test_api_image_cache.py`
- **Fase AAA-4.2 (B.7): rellena la caché local de imágenes bajo demanda. Hasta…** (1 connections) — `src/interfaces/api/main.py`
- **Tests for the on-demand image cache population added in Fase AAA-4.2 (B.7):…** (1 connections) — `tests/integration/test_api_image_cache.py`
- **A tiny real JPEG, standing in for whatever format the shop serves.** (1 connections) — `tests/integration/test_api_image_cache.py`

## Relationships

- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (5 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (4 shared connections)
- [Routers: ProductModel, products.py](Routers-_ProductModel,_products.py.md) (4 shared connections)
- [Api: main.py, deps.py](Api-_main.py,_deps.py.md) (2 shared connections)
- [Dev_tools: sys, run_daily_scan()](Dev_tools-_sys,_run_daily_scan.md) (2 shared connections)
- [Tests: conftest.py, unittest_mock](Tests-_conftest.py,_unittest_mock.md) (2 shared connections)
- [Routers: OfferModel, json](Routers-_OfferModel,_json.md) (1 shared connections)
- [Experimental: render_burn_vfx.py, render_grayskull_vfx.py](Experimental-_render_burn_vfx.py,_render_grayskull_vfx.py.md) (1 shared connections)

## Source Files

- `src/interfaces/api/main.py`
- `tests/integration/test_api_image_cache.py`

## Audit Trail

- EXTRACTED: 42 (95%)
- INFERRED: 2 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*