# ODD Task: Telemetría por Página/Total en 17 Scrapers, Paridad App vs CI y Restauración de Imágenes / Nexus

- **Estado:** `DONE`
- **Glosario e Invariantes:** Ver `docs/CONTEXT.md` y `.agents/AGENTS.md` (Secciones 2 y 3: Prohibición Vintage, Zero-Trust RLS, privacidad de precios manuales).
- **Restricciones Críticas:**
  - Prohibido evadir/resolver CAPTCHAs, Cloudflare Turnstile o retos Imperva.
  - Conservar exactamente `📊 [Resumen] Nuevas en Purgatorio: ...` en `src/infrastructure/scrapers/pipeline.py` (parseado por `frontend/src/components/config/configHelpers.ts`).
  - No añadir sentencias DDL en `init_cloud_db` ni importar `universal_migrator`.

## Criterios de Aceptación Globales
1. **WU1 (Imágenes & Nexus):**
   - `/api/static/images/{product_id}` (y `.webp`) nunca es interceptado por la regex de estáticos de Nginx (`location ^~ /api/` en `nginx.conf` y `nginx.local.conf`), y CSP `connect-src` permite `https://*.supabase.co`.
   - `get_static_image_override` rescata primero imágenes del catálogo local (`data/MOTU/images` / `vintage_images`) convirtiéndolas a WebP en caché, y `_load_product_candidate_image_urls` incluye hermanos `.jpg`/`.png` en `motu-catalog` y `https://` upgrades.
   - `phase0_migration.py`, `phase0_vintage_migration.py`, `personal_collection.py`, `storage_service.py`, `nexus_service.py` y `nexus_vintage_service.py` normalizan rutas contaminadas (`/home/runner/work/...`), corrigen el `IndexError` en modo `'LA'`, validan magic bytes WebP antes de subir y solo actualizan `ProductModel.image_url` tras confirmar subida real en Supabase.
   - `MOTUImage.tsx`, `App.tsx` y `Config.tsx` eliminan el bucle infinito `onError`, usan `/api/static/images/{id}` con `referrerPolicy="no-referrer"`, sincronizan `image_source` en `CacheWelcomeModal` y renderizan fallback limpio al agotar candidatos.
2. **WU2 (Telemetría & Paridad Scrapers):**
   - `BaseScraper._log` antepone siempre `[NombreTienda]` a `log_callback` cuando falta; `_safe_navigate` detecta `PageIndex`, `_sN` y `/page/N`.
   - Los 17 scrapers activos emiten telemetría por página (`📄 [Tienda] ...`) y total final (`📊 [Tienda] ...`) vía `self._log`; `ScrapingPipeline` emite `[Desglose por Tienda]` y errores/timeouts al UI log.
   - `routers/scrapers.py` protege `sync_availability` excluyendo tiendas con `0` resultados; `smythstoys_scraper.py` marca `self.blocked = True` ante fallos de ScraperAPI (`HTTP 500`/red/sin clave); `daily_scan.py` persiste logs en `SessionCloud` y compara `spider_name.lower() == "smythstoys"`.

## Plan de Unidades de Trabajo (Work Units)

| Unidad | Estado | Alcance | Evidencia / Resultado | Límites de Rollback |
| :--- | :--- | :--- | :--- | :--- |
| **WU1** | `DONE` | Restauración Nginx/CSP, ruta sin extensión + rescate local/hermanos `.jpg`, reparación Nexus (`phase0_*`, `StorageService`, `NexusService*`) y `MOTUImage`/UI sin bucle | `test_nexus_and_static_images.py` + `test_api_image_cache.py` + `test_api_perf_wu1_images_gzip.py`: `12 passed in 5.08s`; `npm --prefix frontend run build`: `3755 modules, 13.70s, exit 0` | `frontend/nginx*.conf`, `docker-compose.local-prod.yml`, `src/interfaces/api/main.py`, `src/core/image_utils.py`, `scripts/phase0_*.py`, `personal_collection.py`, `storage_service.py`, `nexus*_service.py`, `frontend/src/{App.tsx,pages/Config.tsx,components/ui/MOTUImage.tsx}` |
| **WU2** | `DONE` | `BaseScraper._log`/`_safe_navigate`, telemetría por página y total en los 17 scrapers, `[Desglose por Tienda]`, protección `sync_availability`, paridad `smythstoys` & `daily_scan.py` | Suite backend conjunta (`8` archivos): `57 passed in 18.52s` (`test_scrapers_telemetry_and_parity.py`: `14 passed`; `test_scrapers_audit_fixes.py`: `12 passed`; `test_smythstoys_scraper.py`: `3 passed`; `test_nexus_and_static_images.py`: `6 passed`; `test_api_image_cache.py`: `4 passed`; `test_api_perf_wu1_images_gzip.py`: `2 passed`; `test_api_db_rls_governance.py`: `6 passed`; `test_backend_bugs_and_perf.py`: `10 passed`); nota: `test_scraper_interface.py` contiene 3 mocks preexistentes obsoletos ajenos a CI | `src/infrastructure/scrapers/{base.py,pipeline.py,*_scraper.py}`, `src/interfaces/api/routers/scrapers.py`, `src/application/jobs/daily_scan.py`, `pyproject.toml` |
