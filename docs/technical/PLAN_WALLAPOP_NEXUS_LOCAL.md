# 🗺️ Plan: Scraper Alternativo de Wallapop (Anti-Bloqueo) + Nexus Local Bridge

> Estado: **Fases 0, 1 y 1.5 COMPLETADAS Y VALIDADAS EN REAL.** Núcleo firmado, fallback
> automático en el cascade (sin gastar ScraperAPI cuando Apify se agota), secreto de firma
> configurable, y tests unitarios + smoke. Pendientes: Fase 2 (Nexus Local Bridge), Fase 3
> (frontend) y Fase 4 (observabilidad).

---

## 1. Problema y causa raíz

El scraper automático `WallapopScraper` falla en producción por **bloqueo WAF de CloudFront (HTTP 403/500)**.
La causa NO es principalmente la técnica de scraping, sino **la reputación de la IP**:

- El servidor corre en **OCI (datacenter)**; CloudFront veta esos rangos de entrada.
- Las cuotas **gratuitas de Apify/ScraperAPI se agotan** rápido.
- Los **proxies públicos** (Geonode/ProxyScrape) son lentos y poco fiables.
- La llamada "directa" del scraper clásico **no firmaba** las peticiones (faltaba `X-Signature`),
  penalización inmediata incluso desde IPs limpias.

**Conclusión:** para resolver el bloqueo de forma fiable hay que (a) firmar bien la API y
(b) **salir por una IP no vetada** (residencial/móvil). Dos formas de conseguir (b):

| Vía | Coste | Fiabilidad | Recomendado para |
| :-- | :-- | :-- | :-- |
| **A. Nexus Local Bridge** (ejecutar el fetch desde el PC del usuario, IP residencial) | **Gratis** | Alta | Uso habitual |
| **B. Proxy residencial "BYO"** (env `WALLAPOP_RESIDENTIAL_PROXY`) | ~€ bajo/mes | Alta | Automatización 24/7 |

---

## 2. Arquitectura

```
                 ┌─────────────────────────┐
   Config Panel  │  POST /api/scrapers/run  │  spider_name = "WallapopManual"
   (web Oráculo) └───────────┬─────────────┘
                             │
          ┌──────────────────┴───────────────────┐
          │        run_scraper_task (orquestador) │
          │        spiders_map["WallapopManual"]  │
          └──────────────────┬───────────────────┘
                             │  .search(query)
                 ┌───────────▼─────────────┐
                 │  WallapopManualScraper   │  ← API v3 FIRMADA (X-Signature) + curl_cffi TLS
                 └───────────┬─────────────┘
             ┌───────────────┴────────────────┐
     IP datacenter (vetada)            WALLAPOP_RESIDENTIAL_PROXY
             │                                │
        ❌ 403 → recomienda            ✅ IP limpia → 200 OK
        Nexus Local Bridge
                 │
     ┌───────────▼───────────────────────────────────────────┐
     │  NEXUS LOCAL BRIDGE (worker en el PC del usuario)       │
     │  - Poll /api/wallapop/jobs/pending                      │
     │  - Ejecuta WallapopManualScraper LOCALMENTE (IP casa)   │
     │  - POST resultados → /api/wallapop/jobs/{id}/results    │
     └───────────┬───────────────────────────────────────────┘
                 │
        pipeline.update_database(offers, ["WallapopManual"])
                 │
             🔥 PURGATORIO (PendingMatchModel, Peer-to-Peer)
```

---

## 3. Núcleo técnico (Fase 0 — HECHO)

Ficheros añadidos:

- `src/infrastructure/scrapers/wallapop_manual_scraper.py` — `WallapopManualScraper(BaseScraper)`:
  - Firma HMAC de la API v3 vía `WallapopSigner` (`X-Signature` + `Timestamp`).
  - Impersonación TLS Chrome con `curl_cffi`.
  - Proxy residencial opcional (`WALLAPOP_RESIDENTIAL_PROXY`).
  - Reutiliza `WallapopScraper._parse_wallapop_json_objects` para normalizar.
  - Multi-keyword en modo `auto` (3 variantes MOTU Origins) + dedupe por URL.
  - `is_auction_source = True` → el pipeline lo enruta al Purgatorio.
- Registro en el orquestador: `src/interfaces/api/routers/scrapers.py` →
  `spiders_map["WallapopManual"] = WallapopManualScraper()`.

Validación real (IP residencial, sin proxy): **9 ofertas MOTU Origins, `blocked=False`**.

---

## 4. Fases pendientes (para el modelo ejecutor)

### Fase 1 — Robustez del núcleo firmado — ✅ COMPLETADA

- [x] **Paginación — investigada empíricamente, NO VIABLE de forma anónima.**
      `/api/v3/search` devuelve `meta.next_page` (JWT opaco con `nextPageParams.offset`,
      `search_id`, etc.). Se probaron 4 combinaciones reales contra la API:
      (a) `next_page` solo, (b) `next_page` + params originales, (c) + `search_id` explícito,
      (d) reintento inmediato para descartar expiración por latencia. **Las 4 devuelven 0
      resultados** — el servidor descarta el contexto de búsqueda y arranca una sesión nueva
      (nuevo `search_id`, nueva `pagination_date`) cada vez. Conclusión: la paginación real
      requiere continuidad de sesión/dispositivo (cookies o `X-DeviceID` de la app autenticada),
      no solo la firma HMAC. **No se implementa bucle de paginación** — sería complejidad sin
      beneficio real. El volumen de resultados sigue viniendo del *fan-out* multi-keyword ya
      existente (3 variantes en modo `auto` → ~9 ofertas/keyword ≈ hasta 27 únicas tras dedupe).
- [x] **Secreto de firma configurable por entorno**: `WallapopSigner.generate_signature` ahora
      resuelve `secret=None` → `os.environ.get("WALLAPOP_SIGN_SECRET") or DEFAULT_SECRET`. Si
      Wallapop rota el secreto del bundle JS, se puede overridear sin tocar código.
- [x] **Tests**: `tests/unit/test_wallapop_signed_api.py` — 7 unit tests offline (firma
      determinista, cambia con el path, override por env, parseo de la estructura real de
      `/api/v3/search`, filtro de ruido, items sin precio) + 1 smoke test opcional marcado
      `@pytest.mark.network` (registrado en `pyproject.toml`, no se ejecuta por defecto).
      Todos verificados en real: `pytest tests/unit/test_wallapop_signed_api.py -m "not network"`
      → 7 passed; `pytest tests/unit/test_wallapop_signed_api.py -m network` → 1 passed (sin bloqueo).

### Fase 1.5 — ⭐ Fallback X-Signature en el CASCADE automático (PRIORITARIA) — ✅ COMPLETADA

> **Estado: IMPLEMENTADA Y VALIDADA EN REAL** (simulando Apify agotado, sin SCRAPERAPI_KEY,
> el cascade devolvió 9 ofertas vía API firmada sin llegar a ScraperAPI). Se creó
> `wallapop_signed_api.py` (núcleo compartido con `SignedSearchResult(offers, blocked)`),
> se refactorizó `WallapopManualScraper` para usarlo, y se insertó el escalón en
> `WallapopScraper.search_via_api` justo tras el bloque `if apify_success: return apify_offers`.

**Qué se implementó:**

1. **`src/infrastructure/scrapers/wallapop_signed_api.py`** (nuevo) — núcleo compartido:
   `search_wallapop_v3_signed(session, query, proxy=None, max_items=40, log_callback=None,
   shop_name_override=None) -> SignedSearchResult(offers, blocked)`. Firma HMAC vía
   `WallapopSigner` sobre `/api/v3/search` (endpoint validado, no `/general/search`),
   `curl_cffi impersonate="chrome120"`, nunca lanza excepción, distingue "vacío" de
   "bloqueado por WAF" (403/429/HTML) mediante el campo `blocked`.
2. **`WallapopManualScraper`** refactorizado para delegar en el núcleo compartido
   (eliminada la duplicación de `_build_headers` / lógica de parseo inline).
3. **`WallapopScraper.search_via_api`** — nuevo escalón "FASE 1.5" insertado justo tras
   `if apify_success: return apify_offers`: intenta la API firmada (con
   `WALLAPOP_RESIDENTIAL_PROXY` si está definida) antes de gastar ScraperAPI; si no hay
   resultados o está bloqueada, continúa el cascade existente sin romper nada.
4. **Import perezoso** dentro de la función para evitar ciclo de imports
   (`wallapop_signed_api` importa `WallapopScraper` a nivel de módulo solo para el parser;
   `wallapop_scraper.py` importa `wallapop_signed_api` en tiempo de ejecución dentro de
   `search_via_api`, no a nivel de módulo).

**Validado en real** (dos veces): `WallapopManualScraper` tras el refactor sigue devolviendo
9 ofertas idénticas; y simulando Apify agotado (`APIFY_TOKEN`/`APIFY_TOKEN2` vacíos) sin
`SCRAPERAPI_KEY`, `WallapopScraper.search_via_api` devolvió 9 ofertas vía API firmada sin
llegar a la Fase 2 (ScraperAPI/proxies/Playwright).

**Nota sobre IP de datacenter:** sin `WALLAPOP_RESIDENTIAL_PROXY`, desde el servidor OCI la
firma sola seguirá dando 403 (IP vetada) — es el comportamiento esperado; este fallback
resuelve "Apify agotado pero la IP es válida", no el veto de IP. Para eso sigue haciendo
falta la Fase 2 (Nexus Local Bridge) o un proxy residencial.

### Fase 2 — Nexus Local Bridge (vía gratuita recomendada)
- [ ] Modelo `WallapopJobModel` (id, query, status[pending|running|done|error], created_at, result_count).
- [ ] Endpoints en `routers/scrapers.py` (o nuevo `routers/wallapop_jobs.py`), protegidos con `verify_api_key`:
  - `POST /api/wallapop/jobs` — encola (query).
  - `GET  /api/wallapop/jobs/pending` — worker toma trabajos.
  - `POST /api/wallapop/jobs/{id}/results` — recibe ofertas y llama `pipeline.update_database`.
  - `GET  /api/wallapop/jobs` — listado/estado para la UI.
- [ ] Worker local `scripts/nexus_local_worker.py` + `run_nexus_bridge.ps1`:
      loop de polling → `WallapopManualScraper().search(query)` local → POST resultados.
- [ ] Alternativa sin worker persistente: reutilizar el `scrape_wallapop_via_cdp.py` ya creado.

### Fase 3 — Frontend (panel de Configuración)
- [ ] Botón "Búsqueda Wallapop (Alternativo)" que dispare `run` con `spider_name="WallapopManual"`
      y campo de `query` (por defecto `auto`).
- [ ] Sección de estado de jobs del Nexus Bridge (si se implementa Fase 2).
- [ ] Documentar `WALLAPOP_RESIDENTIAL_PROXY` en el panel para la vía B.

### Fase 4 — Observabilidad
- [ ] Reutilizar `WallapopIpLogModel` para registrar status (allowed/blocked/proxy_bypass) por ejecución.
- [ ] Mensaje claro en el log en vivo cuando se detecte bloqueo, apuntando al Nexus Local Bridge.

---

## 5. Criterios de aceptación
- Desde el panel, "WallapopManual" devuelve ofertas al Purgatorio **sin 403** cuando:
  (a) se ejecuta vía Nexus Local Bridge, o (b) hay `WALLAPOP_RESIDENTIAL_PROXY` válido.
- **(Fase 1.5)** En el spider automático `Wallapop`, al agotarse Apify se intenta la API v3 firmada
  (X-Signature) **antes** de gastar ScraperAPI; con IP válida devuelve ofertas sin 403.
- Deduplicación correcta y enrutado P2P al Purgatorio.
- Sin regresiones en el resto de spiders del orquestador.

---

## 6. Variables de entorno nuevas
- `WALLAPOP_RESIDENTIAL_PROXY` (opcional) — `http://user:pass@host:port` de proxy residencial/móvil ES.
- `WALLAPOP_SIGN_SECRET` (opcional) — override del secreto de firma si Wallapop lo rota.
