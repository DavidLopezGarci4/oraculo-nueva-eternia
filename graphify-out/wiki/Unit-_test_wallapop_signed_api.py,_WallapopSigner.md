# Unit: test_wallapop_signed_api.py, WallapopSigner

> 19 nodes

## Key Concepts

- **test_wallapop_signed_api.py** (16 connections) — `tests/unit/test_wallapop_signed_api.py`
- **WallapopSigner** (10 connections) — `src/infrastructure/scrapers/wallapop_signer.py`
- **wallapop_signer.py** (9 connections) — `src/infrastructure/scrapers/wallapop_signer.py`
- **._parse_wallapop_json_objects()** (7 connections) — `src/infrastructure/scrapers/wallapop_scraper.py`
- **.generate_signature()** (7 connections) — `src/infrastructure/scrapers/wallapop_signer.py`
- **_build_signed_headers()** (5 connections) — `src/infrastructure/scrapers/wallapop_signed_api.py`
- **test_parse_wallapop_json_objects_extracts_offer()** (3 connections) — `tests/unit/test_wallapop_signed_api.py`
- **test_parse_wallapop_json_objects_filters_junk_keywords()** (3 connections) — `tests/unit/test_wallapop_signed_api.py`
- **test_parse_wallapop_json_objects_skips_missing_price()** (3 connections) — `tests/unit/test_wallapop_signed_api.py`
- **test_signature_changes_with_path()** (3 connections) — `tests/unit/test_wallapop_signed_api.py`
- **test_signature_explicit_secret_still_wins_over_env()** (3 connections) — `tests/unit/test_wallapop_signed_api.py`
- **test_signature_is_deterministic_for_fixed_timestamp()** (3 connections) — `tests/unit/test_wallapop_signed_api.py`
- **test_signature_respects_env_secret_override()** (3 connections) — `tests/unit/test_wallapop_signed_api.py`
- **base64** (2 connections)
- **hmac** (2 connections)
- **Cabeceras de un cliente web real de Wallapop, con X-Signature válida.** (1 connections) — `src/infrastructure/scrapers/wallapop_signed_api.py`
- **Genera la firma X-Signature. Payload: method|path|timestamp** (1 connections) — `src/infrastructure/scrapers/wallapop_signer.py`
- **Generador de firmas X-Signature para la API v3 de Wallapop. Basado en…** (1 connections) — `src/infrastructure/scrapers/wallapop_signer.py`
- **Tests unitarios (offline) para el núcleo firmado de Wallapop (Fase 1 del plan…** (1 connections) — `tests/unit/test_wallapop_signed_api.py`

## Relationships

- [Scrapers: wallapop_scraper.py, WallapopScraper](Scrapers-_wallapop_scraper.py,_WallapopScraper.md) (9 shared connections)
- [Scrapers: asyncio, logging](Scrapers-_asyncio,_logging.md) (5 shared connections)
- [Scripts: models.py, os](Scripts-_models.py,_os.md) (2 shared connections)
- [Scrapers: search_wallapop_section(), test_wallapop_section_api.py](Scrapers-_search_wallapop_section,_test_wallapop_section_api.py.md) (1 shared connections)
- [Scrapers: ScrapedOffer, ._log()](Scrapers-_ScrapedOffer,_._log.md) (1 shared connections)
- [Collectors: hashlib, unique_sheet_name()](Collectors-_hashlib,_unique_sheet_name.md) (1 shared connections)
- [Collectors: personal_vintage_collection.py, time](Collectors-_personal_vintage_collection.py,_time.md) (1 shared connections)
- [Unit: pytest, main()](Unit-_pytest,_main.md) (1 shared connections)
- [Unit: test_search_wallapop_v3_signed_smoke(), network](Unit-_test_search_wallapop_v3_signed_smoke,_network.md) (1 shared connections)
- [Scripts: security.py, check_and_renew_ssl_gh_actions.py](Scripts-_security.py,_check_and_renew_ssl_gh_actions.py.md) (1 shared connections)

## Source Files

- `src/infrastructure/scrapers/wallapop_scraper.py`
- `src/infrastructure/scrapers/wallapop_signed_api.py`
- `src/infrastructure/scrapers/wallapop_signer.py`
- `tests/unit/test_wallapop_signed_api.py`

## Audit Trail

- EXTRACTED: 45 (85%)
- INFERRED: 8 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*