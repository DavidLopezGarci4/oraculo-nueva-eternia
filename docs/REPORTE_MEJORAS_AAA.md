# Reporte-Prompt · Elevación a Triple-A — El Oráculo de Nueva Eternia

> **Propósito de este documento.** No es un simple listado de bugs: es un **plan de trabajo ejecutable**, ordenado por el flujo en el que deben abordarse las tareas. Cada acción está redactada como un "prompt" autónomo (con archivos y contexto) que puedes entregar a una IA o a un desarrollador para ejecutarla directamente. Las fases están ordenadas por dependencia y riesgo: **seguridad primero (bloqueante), luego arquitectura, después rendimiento y por último diseño/pulido AAA.**
>
> Fecha de análisis: 2026-07-21 · Rama: `main` · Alcance: backend (FastAPI), frontend (React 19 + Vite 7), despliegue (Docker/nginx), datos (SQLite/Supabase).

---

## Estado de ejecución (actualizado 2026-07-21)

> Trabajado en la rama `refactor/aaa-uplift`, commit por commit, con `pytest` + `npm run build` + un security-review independiente verificando cada paso antes de avanzar. Si retomas este trabajo en otra máquina/sesión: `git log --oneline` en esa rama es la fuente de verdad, esto es solo un resumen de alto nivel.
>
> **Antes de tocar nada**, lee **[.claude/skills/aaa-buenas-practicas/SKILL.md](../.claude/skills/aaa-buenas-practicas/SKILL.md)** — protocolo de arranque de sesión, límites de seguridad no negociables y las convenciones de código/testing/migraciones/documentación que rigen todo el trabajo de este backlog. Viaja versionado con el repo, así que está disponible en cualquier máquina.

- ✅ **Fase 0 — Preparación:** hecha. Línea base de métricas en [BASELINE_METRICS.md](BASELINE_METRICS.md), `local_collection_dump.json` desindexado.
- ✅ **Fase 1 — Seguridad crítica:** hecha por completo (1.1–1.9). Clave de admin fuera del bundle, JWT real en el frontend, IDOR cerrado en `collection.py`/`vault.py`/`logistics.py`, path traversal corregido, CORS restringido, guardián de secretos de producción, bypass de login eliminado, rate limiting en auth, cabeceras de seguridad en nginx.
- ✅ **Fase 2 — Backend hardening:** hecha por completo.
  - 2.1: auditoría de los 89 endpoints — encontró y cerró un IDOR grave adicional en `users.py` (activación no autenticada del escaparate público de cualquier usuario).
  - 2.2: `response_model` estricto en `users.py`/`dashboard.py` (los routers tocados en 2.1). El resto de routers se completó como Ola 3 / 3b (ver checklist abajo) — a 2026-07-21, **todos** los routers tienen `response_model` salvo los endpoints deliberadamente excluidos (binarios/streaming o datos genuinamente dinámicos).
  - 2.3: adopción real de Alembic preparada y probada localmente (migración idempotente + `docker-entrypoint.sh` + guía paso a paso en [ALEMBIC_ADOPTION.md](ALEMBIC_ADOPTION.md)) — **pendiente de que ejecutes tú los pasos en la máquina con Docker**, no se ha tocado ninguna base de datos real de producción.
  - 2.4: errores de arranque silenciosos eliminados (`config.py`, `database_cloud.py`).
  - 2.5: supervisión con reintentos del listener de Telegram.
  - 2.6: dependencias fijadas en `requirements.txt`.
  - **Bonus/fix crítico encontrado en el camino:** el guardián de secretos de producción de la Fase 1.5 no se activaba nunca en el despliegue real (`docker-compose.prod.yml` usa `ENV=production`, el código comprobaba `ENVIRONMENT`) — corregido.
- ✅ **Fase 3.1 — Router real (frontend):** hecha y verificada en navegador real (no solo build). `react-router-dom` sustituye `activeTab` + *keep-alive*; cada página monta/desmonta de verdad al navegar (confirmado por JS que el DOM de una página anterior desaparece por completo). `Sidebar.tsx`/`Navbar.tsx` no se tocaron (adaptador de compatibilidad). Guard de `/purgatory` ahora declarativo en la ruta.
  - ⏸️ **Fase 3.2 — pendiente:** trocear `Config.tsx` (3072 líneas), `Purgatory.tsx` (2253) y `Catalog.tsx` (1965). Es el ítem más grande y de mayor riesgo de todo el plan; se dejó deliberadamente para el final/una sesión dedicada.
- 🟡 **Fase 4 — Rendimiento: parcial, lo de mayor impacto/menor riesgo ya hecho.**
  - 4.1 ✅ `manualChunks` en `vite.config.ts` — el chunk de entrada bajó de 154.94 KB a 88.70 KB gzip.
  - 4.2 ✅ (parcial) 16 imágenes sin usar eliminadas de `frontend/src/assets` (18 MB → 412 KB, verificado sin imágenes rotas en navegador). ✅ Cerrado el hueco por el que las imágenes nuevas de los scrapers de tienda nunca se convertían a WebP (`main.py::_fetch_and_cache_product_image`, probado con 4 tests). Pendiente: favicon/audio en `public/` (bajo impacto).
  - 4.3 — revisado; los tiempos de caché de React Query ya están bien ajustados donde importa (p.ej. `Purgatory.tsx` tiene un `staleTime`/`refetchInterval` deliberado con comentario explícito para no romper la UX de curación). No se encontró un problema concreto que justifique tocarlo.
  - 4.4 ✅ Precarga de página al pasar el ratón por el sidebar (verificado con la Performance API del navegador: el chunk se descarga antes del clic).
  - 4.5 ⏸️ pendiente — virtualización de listas largas en Catálogo/Colección.
  - 4.6 ✅ ya estaba hecho (colado en la Fase 1: `Cache-Control: immutable` en nginx para assets con hash).

---

## 🎯 BACKLOG CONSOLIDADO Y PRIORIZADO (fuente única de verdad — actualizado 2026-07-21)

> **Por qué esta sección.** El trabajo pendiente estaba disperso en tres sitios que se solapaban y contradecían (`Apuntes a llevar a cabo.txt` B.1–B.9, el antiguo "checklist de continuidad", y las Fases 5–8 de más abajo). Además, **tres fases enteras (5 accesibilidad/UX, 6 datos, 7 tests/CI) no aparecían en ningún checklist de pendientes** — parecía que quedaban 4 cosas cuando en realidad quedan bastantes más. Esto lo unifica todo, verificado contra el código real, y lo ordena por **olas de ejecución** (impacto ÷ esfuerzo ÷ riesgo). **Ejecuta de arriba a abajo.**
>
> Leyenda: 🟢 bajo · 🟡 medio · 🔴 alto (esfuerzo/riesgo).

### 🚨 OLA 0 — Emergencia de seguridad (HOY, acción del usuario) — reordenada tras el intento de acceso del 2026-07-21

La rama `refactor/aaa-uplift` corrige todo, pero **no protege nada hasta que se despliegue Y se roten los secretos**. Hoy `main` (lo desplegado) todavía lleva `eternia-shield-2026` embebida en el bundle (`admin.ts:5`, `purgatory.ts:5`) y esa clave está también en el historial de git.

- [ ] **0.A — Rotar `ORACULO_API_KEY` en el `.env` de producción y reiniciar el backend.** Es "cambiar la cerradura": la clave pública deja de funcionar al instante incluso con el código viejo. No necesita Docker ni desplegar la rama. Genera valor: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
- [ ] **0.B — Rotar `JWT_SECRET` igual** (invalida sesiones que un atacante hubiera podido crear).
- [ ] **0.C — Si el repo de GitHub es PÚBLICO:** ponlo privado, o purga la clave del historial (`git filter-repo`). Mientras sea público, la clave vieja es legible aunque se borre del código. (Da igual una vez rotada en 0.A, pero conviene no dejar rastro.)
- [ ] **0.D — Revisar `WallapopIpLogModel` / alertas de Telegram** para ver el ID/IP del intento y confirmar si el "Escudo" (device shield) lo bloqueó o si hubo acceso real.

### 🚀 OLA 1 — Desplegar lo ya construido (activa TODO el blindaje) — usuario, en la máquina con Docker

Esto es lo de **mayor retorno de todo el backlog**: hay ~19 commits de seguridad ya escritos y probados que no protegen nada hasta desplegarse. Sigue `Apuntes a llevar a cabo.txt` Parte A (backups → rama → rotar secretos → migración Alembic → `docker compose up -d --build` → verificar login). Guía de BD en [ALEMBIC_ADOPTION.md](ALEMBIC_ADOPTION.md).

### ✅ OLA 2 — Quick wins de código — COMPLETA (2026-07-21)

| # | Tarea | Estado |
|---|-------|--------|
| 2a | CI que de verdad corra la suite | ✅ `ci.yml`: job `backend` (`pytest tests/ -v`) + job `frontend` (`npm ci && npm run build && npm audit --audit-level=high`), en paralelo. Verificados los 3 comandos localmente antes de comitear. |
| 2b | `lang="es"` + meta description + Open Graph | ✅ `frontend/index.html`. Verificado en navegador: `document.documentElement.lang === "es"`, meta/OG presentes. |
| 2c | Fix `backup_db.ps1` (modo WAL) | ✅ Sustituido `Copy-Item` por `sqlite3.backup()` vía Python (API de backup online, consistente en modo WAL). Ejecutado de verdad contra la BD real: backup válido con 23 tablas y datos reales. |
| 2d | `prefers-reduced-motion` | ✅ `<MotionConfig reducedMotion="user">` global en `main.tsx` — respeta la preferencia del SO en todos los componentes `motion.*` sin tocar cada animación. |
| 2e | (solo máquina local) columna `offers.image_url` en `oraculo.db` | ✅ Aplicado con `ALTER TABLE`. Verificado: `/api/products` pasó de 500 a 200. No aplica a producción (dato de runtime, no versionado). |

Commits: `b6b6d49` (2a), `9a2d95a` (2b+2c+2d). pytest 49/49 en verde en cada paso.

### ✅ OLA 3 — Valor medio, esfuerzo medio — COMPLETA (2026-07-21)

| # | Tarea | Por qué | Archivos | Esf./Riesgo |
|---|-------|---------|----------|-------------|
| 3a | **`datetime.utcnow()` → `datetime.now(timezone.utc)`** | ✅ **COMPLETA (2026-07-21).** 51 usos reales en 20 archivos (16 en `src/`, 4 más en `scripts/` de mantenimiento/diagnóstico no listados originalmente). **Riesgo real confirmado**: SQLite vía SQLAlchemy siempre devuelve `datetime` naive al leer una columna `DateTime` sin `timezone=True` — aunque se escriba un valor aware, se pierde el `tzinfo` al releer (verificado empíricamente). Comparar un `datetime.now(timezone.utc)` (aware) contra un valor leído de la BD (naive, ej. `offer.last_seen`, `alert.last_notified_at`) lanza `TypeError` en runtime. Por eso el reemplazo elegido en TODO el barrido es `datetime.now(timezone.utc).replace(tzinfo=None)` — produce el mismo valor naive-UTC que `datetime.utcnow()` (mismo instante, mismo tipo), así que es un cambio de comportamiento cero: solo deja de llamar a la función obsoleta, sin arriesgar mezclar naive/aware en ninguna de las comparaciones/restas ya existentes (`pipeline.py`, `notifier.py`, `market_intelligence.py`). Verificado: suite completa 63/63 **sin ningún warning de deprecación** (antes había 2 `DeprecationWarning` reales en cada run), `.venv/Scripts/python.exe -m py_compile` limpio en los 20 archivos, y `grep` confirma cero usos de `datetime.utcnow()` en todo el repo (solo quedan menciones en prosa dentro de `docs/`). (B.8) | 16 archivos en `src/` + 4 en `scripts/` | ✅ |
| 3b | **`response_model` en el resto de routers** | ✅ **COMPLETA (2026-07-21).** Contrato de API estricto = no fuga de campos internos + docs OpenAPI. Cubiertos todos los routers: `users`, `dashboard`, `admin`(14/14), `products`(15/15 salvo 2 endpoints de datos dinámicos externos, deliberado), `purgatory`(12/12), `scrapers`(salvo `/run`/`/stop`, deliberado — ejecutarían red/procesos reales en test), `vault`(salvo exports binarios), `wallapop_jobs`, `system`(salvo `system_audit`/`get_sword_configs`, dinámicos), `logistics`, `showcase`, `auth`, `collection`(salvo 3 exports binarios). Verificado con la suite COMPLETA (58/58) en cada paso — el estado compartido de la BD de test revela mismatches que el camino vacío oculta. Añadido `PurgatoryItemOutput`/`PurgatorySuggestionOutput` (schema anidado, el de mayor riesgo) con test de datos reales forzando un EAN match. (2.2 / B.3) | `src/interfaces/api/routers/*.py`, `schemas.py` | ✅ |
| 3c | **Accesibilidad WCAG (auditoría axe)** | ✅ **COMPLETA (2026-07-21).** Auditoría real con `axe-core` 4.10.2 inyectado en el navegador (no solo lectura de código) contra la app corriendo de verdad: login, registro, dashboard, catálogo, colección, ajustes (todas las pestañas alcanzables) y el Santuario público (`/santuario/:username`, sin login) — verificado de extremo a extremo registrando una cuenta desechable, aprobando su dispositivo vía la API admin real, y activando su propio Santuario público con el switch ya arreglado. **10 tipos de violación reales encontrados y corregidos** (antes: `button-name` crítico en botones-icono sin `aria-label`, `label`/`label-title-only` crítico en `<select>`/`<input>` sin asociación programática, `landmark-unique`/`region` moderado por contenido fuera de `<main>`/`<nav>` sin etiquetar). Nuevo hook compartido `frontend/src/hooks/useModalA11y.ts` (foco atrapado con Tab/Shift+Tab, cierre con Escape, foco devuelto al cerrar) aplicado a los **10 modales** de la app (`CacheWelcomeModal`, `QuickPreviewModal`, `MarketIntelligenceModal`, `CollectionItemDetailModal` + su lightbox de imagen, y los 3 de `Config.tsx` + 2 de `Purgatory.tsx`) con `role="dialog"`/`"alertdialog"` + `aria-modal` + `aria-labelledby`. `aria-label` añadido a ~20 botones/enlaces-icono y 6 `<select>`, `htmlFor`/`id` en ~15 pares label/input sin asociar, `role="switch"`+`aria-checked` en el toggle de Santuario Público, `<main>` añadido a `LoginPage`/`MasterLogin`/`Showcase` (con `aria-hidden` en fondos decorativos). Verificado con `tsc -b --noEmit` limpio tras cada tanda y **0 violaciones de axe** en cada página re-escaneada. **Gap conocido**: los 2 modales de `Purgatory.tsx` y la pestaña de gestión de usuarios de `Config.tsx` (solo admin) se corrigieron con el mismo patrón ya probado pero NO se verificaron en vivo — el bloqueador de permisos del entorno impidió promover la cuenta de prueba a admin vía la API. Contraste de color no auditado (`axe` no lo marcó como violación en las páginas alcanzadas; queda para una revisión visual manual futura si se detecta algún caso). (Fase 5.1) | `frontend/src/hooks/useModalA11y.ts`, `pages/*.tsx`, `components/**/*.tsx` | ✅ |
| 3d | **Auth en `/api/wallapop/import`** | ✅ **COMPLETA (2026-07-21).** Guardián dual `verify_wallapop_import` (`deps.py`): la extensión de Chrome manda su propia clave de bajo privilegio (`X-Extension-Key` / `EXTENSION_API_KEY`, distinta de `ORACULO_API_KEY` — si se filtra desde el navegador no da acceso admin), o cae al flujo normal `verify_device` para el import manual desde la SPA ya autenticada (Purgatory). Popup de la extensión actualizado con el campo de clave; `.env.example` y el guardián de secretos de producción también. 5 tests nuevos en `test_api_permissions.py` (sin auth → 403, key equivocada → 403, key correcta → 200, dispositivo aprobado → 200, dispositivo pendiente → 403). Suite completa: 63/63. (B.2) | `deps.py`, `config.py`, `users.py`, `chrome-extension/*` | ✅ |
| 3e | **Revisar índices de BD** | ✅ **COMPLETA (2026-07-21).** `EXPLAIN QUERY PLAN` contra las consultas reales de catálogo/colección/purgatorio encontró 9 huecos confirmados (`SCAN` de tabla completa o `TEMP B-TREE` para el `ORDER BY`): `products.category`, `offers.last_seen`/`opportunity_score`, `collection_items.acquired`, `pending_matches.validation_status`/`found_at`, `offer_history.timestamp`, `price_history.offer_id`/`recorded_at`. Añadido `index=True` en `models.py` (46 → 55) y migración Alembic idempotente (`feac3ac24f77`, comprueba índices existentes antes de crear cada uno — mismo patrón que `d4283e0fbed1`). Verificada aplicando/revirtiendo/reaplicando contra una copia real de `oraculo.db` baselineada en el head anterior. Suite completa: 63/63 (no afectada, usa `create_all`). (Fase 6.1) | `src/domain/models.py`, `migrations/versions/feac3ac24f77_*.py` | ✅ |

### 🔴 OLA 4 — Refactor grande (sesión dedicada, alto riesgo de regresión)

- **4a — Trocear `Config.tsx` (3073 líneas), `Purgatory.tsx` (2253), `Catalog.tsx` (1965)** en subcomponentes + hooks. Es mantenibilidad, NO rendimiento (el router real de la Fase 3.1 ya resolvió el problema de memoria). Hacer archivo por archivo, verificando en navegador cada paso. (3.2 / B.4) — ✅ **ÍTEM COMPLETO (2026-07-21).** Los 3 monolitos troceados.
  - ✅ **`Config.tsx` COMPLETO (2026-07-21).** 3101 → 886 líneas (-71%), en 5 commits incrementales, cada uno con `tsc -b --noEmit` + `npm run build` + verificación en navegador (0 violaciones de axe) antes de avanzar. `Config.tsx` pasó de "God Component" a un orquestador de estado/efectos que renderiza 5 pestañas + 5 modales, todos nuevos en `frontend/src/components/config/` (11 archivos): `AddUserModal`, `ResetConfirmModal`, `IpLogsModal`, `VintageCalibratorModal`, `ModernCalibratorModal`, `UsersTab`, `SystemTab`, `InventoryTab`, `ScrapersTab`, `configHelpers.ts`. Extracción mecánica 1:1 (mismo estado/handlers vía props, sin re-arquitecturar `fetchData` ni la lógica de negocio) — deliberado, para minimizar riesgo de regresión. **Gap de verificación honesto**: las pestañas `scrapers` e `inventory` (2 de 5) son solo accesibles con cuenta admin; el clasificador de permisos del entorno bloqueó promover la cuenta de prueba, así que quedan verificadas solo por tipos (`tsc`) y por lectura cuidadosa del código, no probadas en vivo en el navegador — pendiente de que las pruebes tú con tu cuenta admin real.
  - ✅ **`Purgatory.tsx` COMPLETO (2026-07-21).** 2276 → 923 líneas (-59%), en 4 commits incrementales, cada uno con `tsc -b --noEmit` + `npm run build` antes de avanzar. Nuevos archivos en `frontend/src/components/purgatory/` (4): `SwipeCard` (ya estaba aislado a nivel de módulo, solo se movió de fichero), `ForensicModal`, `VintageClassifyModal` (el bloque JSX más grande, ~370 líneas), `PurgatoryToolbar` (cabecera + buscador + filtros). El modo lista se extrajo como `PurgatoryListView`. Extracción mecánica 1:1, igual que `Config.tsx`; las mutaciones de React Query (`matchMutation`, `matchVintageMutation`, etc.) se quedan en el padre porque las comparten varias vistas, y se pasan tipadas como prop con `UseMutationResult<...>`. **Gap de verificación honesto**: `/purgatory` está gateado a `isAdminUser` en `App.tsx` y la cuenta de prueba no es admin, así que ninguna parte de este archivo se pudo probar en el navegador (mismo bloqueador de permisos que en Config.tsx) — verificado solo por `tsc` + build + lectura cuidadosa del código; pendiente de que lo pruebes tú con tu cuenta admin real.
  - ✅ **`Catalog.tsx` COMPLETO (2026-07-21).** 1965 → 887 líneas (-55%), en 5 commits incrementales, cada uno con `tsc -b --noEmit` + `npm run build` antes de avanzar. Nuevos archivos en `frontend/src/components/catalog/` (9): `CustomTooltip` y `catalogHelpers.ts` (`buildSearchQuery`, ya aislados a nivel de módulo), `CronosView` (pestaña de comparación de historial de precios, con recharts), `ProductDetailModal` (analítica de precios + panel de fusión de figuras, el bloque más grande), `EditProductModal`, `FullscreenImageModal`, `VintageSyncModal` (los 3 admin-only), `ProductCard` (tarjeta individual del grid, incluyendo el helper puro `getSentimentBadge` que solo usaba ella). Extracción mecánica 1:1. A diferencia de Config/Purgatory, `Catalog.tsx` **sí es alcanzable con la cuenta de prueba no-admin** (`/catalog`), así que se verificó en vivo en el navegador tras cada extracción relevante: carga sin errores de boundary, pestaña Cronos interactiva (el campo de búsqueda actualiza estado correctamente), 0 errores nuevos en consola tras hard-reload. Único gap: los 2 modales admin-only (`EditProductModal`, `VintageSyncModal`) y el panel de fusión dentro de `ProductDetailModal` no se pudieron probar interactivamente (misma cuenta no-admin), solo por tipos/build.
- **4b — Virtualizar listas largas** (`@tanstack/react-virtual`) en Catálogo/Colección/Purgatorio para no renderizar cientos de tarjetas de golpe. Toca `Catalog.tsx`, encaja con 4a. (4.5 / B.5)

### 🏁 OLA 5 — Verificación final AAA (Fase 8, tras desplegar)

- Lighthouse (Performance ≥ 90, Accessibility ≥ 95) en `dashboard`/`catalog`/`collection`; LCP < 2.5 s; `/security-review` sin críticos/altos; `pip-audit` + `npm audit` limpios. Registrar el "después" en [BASELINE_METRICS.md](BASELINE_METRICS.md).
  - ✅ **`pip-audit` + `npm audit` COMPLETO (2026-07-21).** `npm audit` en `frontend/` ya estaba limpio (0 vulnerabilidades). `pip-audit -r requirements.txt` encontró **20 vulnerabilidades conocidas en 3 paquetes**: `PyJWT` 2.10.1 (librería de auth, múltiples CVEs), `pydantic-settings` 2.12.0, y `starlette` 0.50.0 (transitiva de `fastapi`, capada a `<0.51.0` por `fastapi==0.128.0`, así que hizo falta subir también `fastapi` a 0.139.2 — sin tope superior de `starlette` — para poder llegar a `starlette==1.3.1`, el mínimo que corrige sus CVEs). Verificado con la suite completa (63 tests, en verde antes y después de cada bump) y arranque real de `uvicorn` sirviendo `/docs` + `/openapi.json` con 200 OK. `pip-audit` re-ejecutado tras el cambio: **0 vulnerabilidades**. Único efecto colateral: warning de deprecación de `starlette.testclient` sobre `httpx` (no bloqueante, sin acción por ahora).
  - ⏸️ Lighthouse, LCP y `/security-review` siguen pendientes de que despliegues (dependen de un entorno real, no del dev local vacío).
- **4b — Virtualizar listas largas** (`@tanstack/react-virtual`) en Catálogo/Colección/Purgatorio: **deliberadamente pospuesto.** A diferencia de las extracciones mecánicas de 4a (mismo comportamiento, solo movido de fichero), virtualizar el grid responsive de `Catalog.tsx` (`grid-cols-2 sm:... lg:grid-cols-3 xl:grid-cols-4 landscape:grid-cols-3`) es un cambio de arquitectura de renderizado que necesita datos reales para verificar que no rompe el layout — la base de datos de desarrollo está vacía, así que no se pudo comprobar visualmente. Recomendación técnica para cuando se retome: virtualización por filas (`useVirtualizer` de `@tanstack/react-virtual` con `count = Math.ceil(items.length / columnasActuales)`), detectando el número de columnas actual vía `ResizeObserver`/`matchMedia` en vez de asumirlo fijo, y probándolo con datos reales antes de mergear.

### ⚪ Descartado / no merece la pena ahora

- Compresión de `public/oraculo-logo.png` (favicon, se mantiene PNG por compatibilidad) y `public/theme.mp3` (8.2 MB de audio; recomprimir solo si molesta el peso). — Bajo impacto.
- Ajuste de `staleTime`/`gcTime` de React Query (4.3): revisado, ya está bien donde importa; no hay problema concreto que arreglar.

### 📋 Revisión de documentación pendiente

- **B.9** — Leer completos `docs/DOCUMENTACION_MAESTRA.md` (617 líneas) y `docs/MASTER_ROADMAP.md` (549) por si quedan afirmaciones desfasadas sin descubrir (hoy solo se revisaron por búsqueda dirigida).

---

## Resumen ejecutivo — dónde está la aplicación hoy

**Stack (moderno y correcto en su base):** FastAPI + SQLAlchemy 2 + Pydantic v2 · React 19 + Vite 7 + Tailwind 4 + React Query + framer-motion + recharts · arquitectura por capas (`domain/application/infrastructure/interfaces`) · Docker + nginx + Supabase/Postgres en prod, SQLite en local.

**Diagnóstico global:** la base tecnológica es buena, pero el proyecto arrastra deuda que hoy **impide el nivel AAA en tres ejes**:

| Eje | Estado actual | Bloqueante para AAA |
|-----|---------------|---------------------|
| 🔴 **Seguridad** | Modelo de autenticación efectivamente inexistente en el borde real. Clave maestra hardcodeada en el bundle del navegador. IDOR generalizado. CORS abierto. Sin cabeceras de seguridad. | **SÍ — crítico** |
| 🟠 **Arquitectura** | Páginas monolíticas (`Config.tsx` 3072 líneas, `Purgatory.tsx` 2253, `Catalog.tsx` 1965). Sin router real; navegación por `activeTab` + *keep-alive* que mantiene todas las secciones montadas. Auth 100% client-side. | Parcial |
| 🟡 **Rendimiento** | Bundle principal único de **1.23 MB**, `dist` de **18 MB**, **17 MB de PNG** sin optimizar (con duplicados). Todas las secciones visitadas quedan vivas en memoria y siguen refetcheando. | Sí (métricas AAA) |

**Prioridad de ejecución:** Fase 1 (seguridad) es **no negociable y debe ir primero**. Fases 2–4 (arquitectura + rendimiento) dan el "baño de cara". Fase 5 (diseño/UX) es el pulido final AAA.

---

## FASE 0 · Preparación y línea base (antes de tocar nada)

**Objetivo:** poder medir la mejora y trabajar sin romper.

- **0.1 — Congelar métricas de partida.** Ejecuta `npm run build` en `frontend/` y anota: tamaño de cada chunk, tamaño total de `dist`, y una traza Lighthouse (Performance, Accessibility, Best-Practices, SEO) de las rutas principales (`dashboard`, `catalog`, `collection`). Guárdalas en `docs/BASELINE_METRICS.md`. Sin línea base no se puede demostrar "AAA".
- **0.2 — Rama de trabajo.** Crea `git checkout -b refactor/aaa-uplift`. Todo el trabajo de este reporte vive aquí hasta validación.
- **0.3 — Inventario de secretos.** Verifica que `.env` NO está en git (`git ls-files | grep .env`). Rota **ya** cualquier secreto que haya podido llegar a un commit: `JWT_SECRET`, `ORACULO_API_KEY`, `TELEGRAM_BOT_TOKEN`, `SUPABASE_SERVICE_ROLE_KEY`, `SMTP_PASS`, `CLOUDINARY_API_SECRET`, `SCRAPERAPI_KEY`. Nota: el commit `5390811` ya tuvo que desindexar `scratch/` por fuga de secretos de caché de Chrome → asume que hay exposición histórica y rota.

---

## FASE 1 · Seguridad crítica (BLOQUEANTE — hacer primero)

> Esta fase corrige fallos que hoy hacen que **cualquier persona con acceso a la URL tenga control total de la aplicación**. Nada de lo demás importa hasta cerrar esto.

### 1.1 — 🔴 CRÍTICO: clave maestra de administración hardcodeada en el frontend
- **Dónde:** `frontend/src/api/admin.ts:5` y `frontend/src/api/purgatory.ts:5` → `const API_KEY = import.meta.env.VITE_ORACULO_API_KEY || 'eternia-shield-2026'`.
- **Problema:** ese valor por defecto se **compila dentro del bundle JS** que se envía a todos los navegadores. Cualquiera puede abrir DevTools, leer `eternia-shield-2026` y usarlo. Y esa misma clave, en el backend (`auth.py:146`), otorga **bypass soberano de login** (`request.password == settings.ORACULO_API_KEY` → acceso admin) y en `deps.py:87` **suplanta al usuario admin**. Es decir: la clave de dios está publicada.
- **Acción (prompt):** *"Elimina el fallback `'eternia-shield-2026'` de `admin.ts` y `purgatory.ts`. El frontend NO debe enviar nunca la API key de administración. Reemplaza el modelo por: el frontend hace login → recibe un JWT → envía `Authorization: Bearer <jwt>` en un interceptor de axios central. La `ORACULO_API_KEY` pasa a ser un secreto exclusivamente servidor-a-servidor (scrapers/workers), nunca navegador. Rota el valor de la clave tras el cambio."*

### 1.2 — 🔴 CRÍTICO: autenticación real ausente en routers de datos
- **Dónde:** `collection.py` (6 endpoints, **0 `Depends`**), `vault.py` (4 endpoints, **0 `Depends`**), `auth.py`, `logistics.py`, `showcase.py`.
- **Problema:** endpoints como `GET /api/collection?user_id=<n>` reciben el `user_id` **como parámetro de query sin verificar identidad** (`collection.py:57`). Cualquiera puede leer/exportar la colección de cualquier usuario cambiando el número → **IDOR** (Broken Object Level Authorization, OWASP API #1). El *keep-alive* del front no protege nada; la API está desnuda.
- **Acción (prompt):** *"Añade `current_user: UserModel = Depends(get_current_user)` a TODOS los endpoints de `collection.py`, `vault.py`, `logistics.py`. Deriva el `user_id` del token (`current_user.id`), nunca del query param. Donde un admin necesite actuar sobre otro usuario, exige rol admin explícito (`Depends(require_admin)`). Elimina los parámetros `user_id: int` de la firma pública."*

### 1.3 — 🔴 CRÍTICO: acceso arbitrario a ficheros vía `file_path`
- **Dónde:** `vault.py:35` → `api_stage_vault(user_id: int = 2, file_path: str = None)`.
- **Problema:** un `file_path` controlado por el cliente que llega a operaciones de fichero es **path traversal / lectura-escritura arbitraria**. Igual, el endpoint de imágenes `main.py:58` (`get_static_image_override`) acepta `user_id=2` por defecto y arma rutas con `os.path.join(custom_dir, ...)` desde datos de BD.
- **Acción (prompt):** *"Elimina `file_path` como parámetro de entrada del cliente en `vault.py`; el servidor debe resolver la ruta internamente contra un directorio permitido (allowlist) y validar con `Path.resolve()` que queda dentro de la carpeta base. Aplica la misma validación anti-traversal en `main.py:get_static_image_override` y protégelo con autenticación."*

### 1.4 — 🟠 ALTO: CORS totalmente abierto con credenciales
- **Dónde:** `main.py:93-99` → `allow_origins=["*"]` + `allow_credentials=True` + `allow_methods=["*"]` + `allow_headers=["*"]`.
- **Problema:** combinación inválida/insegura; expone la API a cualquier origen. Con credenciales, es un vector de robo de sesión.
- **Acción (prompt):** *"Sustituye `allow_origins=['*']` por una lista blanca desde settings (`settings.CORS_ORIGINS`), p. ej. `['https://oraculo-eternia.duckdns.org']` en prod y `http://localhost:3001` en dev. Restringe `allow_methods`/`allow_headers` a los realmente usados."*

### 1.5 — 🟠 ALTO: secretos con valores por defecto inseguros en código
- **Dónde:** `config.py:33` (`ORACULO_API_KEY = "eternia-shield-2026"`), `config.py:50` (`JWT_SECRET = "...CHANGE-IN-PRODUCTION"`). `main.py:9` solo *loguea* la advertencia, no impide arrancar.
- **Acción (prompt):** *"Haz que `JWT_SECRET` y `ORACULO_API_KEY` NO tengan default utilizable: si en modo no-DEBUG están vacíos o son el valor de ejemplo, la app debe abortar el arranque (`sys.exit`), no solo advertir. Documenta su generación con `secrets.token_urlsafe(48)`."*

### 1.6 — 🟠 ALTO: "identidad soberana" y bypass de login por API key
- **Dónde:** `auth.py:127-185` (login con `is_sovereign_bypass = request.password == settings.ORACULO_API_KEY` y transferencia silenciosa a admin) y `deps.py:81-93` (API key → devuelve el primer usuario admin).
- **Problema:** múltiples puertas traseras que colapsan el modelo de roles. Un password igual a la API key = admin en cualquier cuenta.
- **Acción (prompt):** *"Elimina el mecanismo de 'sovereign bypass' por password. Autenticación = contraseña verificada con PBKDF2 y punto. Si se requiere un canal admin de servicio, que sea un endpoint separado protegido por API key server-side y por IP allowlist, jamás mezclado con el login de usuarios."*

### 1.7 — 🟠 ALTO: sin cabeceras de seguridad ni rate-limiting
- **Dónde:** `frontend/nginx.conf` no define `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`. No hay throttling en `/api/auth/*`.
- **Acción (prompt):** *"Añade en el bloque `server 443` de nginx.conf las cabeceras HSTS, X-Content-Type-Options=nosniff, X-Frame-Options=DENY, Referrer-Policy=strict-origin-when-cross-origin, Permissions-Policy y una CSP acorde. En el backend, añade rate-limiting (p. ej. `slowapi`) a login/forgot-password/reset-password para frenar fuerza bruta y enumeración."*

### 1.8 — 🟡 MEDIO: dispositivos auto-autorizados y endpoint que lista usuarios
- **Dónde:** `deps.py:36-52` (una API key válida **auto-registra y auto-autoriza** cualquier `X-Device-ID` → el "Escudo 3OX" no protege si la key está publicada) y `auth.py:188` (`GET /api/auth/users` devuelve toda la lista de usuarios sin auth → enumeración).
- **Acción (prompt):** *"Tras cerrar 1.1, revisa que el auto-autorizado de dispositivos ya no sea explotable. Protege o elimina `GET /api/auth/users` (fuga de usuarios/roles). Si es solo para el selector de test, gcategóriza detrás de rol admin."*

### 1.9 — Verificación de la fase
- **Acción (prompt):** *"Ejecuta la skill `/security-review` sobre la rama y corre `pip-audit`/`npm audit`. Añade un test de integración que confirme que `GET /api/collection?user_id=<otro>` devuelve 401/403 sin token válido."*

---

## FASE 2 · Endurecimiento del backend y contrato de API

> Con la seguridad cerrada, se estabiliza el backend para que soporte crecimiento y sea mantenible.

- **2.1 — Centralizar dependencias de auth.** Crea `require_admin` y `require_user` en `deps.py` y aplícalos de forma consistente (hoy la protección es dispar: `admin.py` 14/14, pero `collection.py` 0/6). *Prompt: "Audita los 89 endpoints y documenta en una tabla qué rol exige cada uno; aplica el `Depends` correspondiente."*
- **2.2 — Esquemas de respuesta estrictos.** Varios endpoints devuelven `dict` crudos con campos internos. *Prompt: "Define `response_model` Pydantic en todos los endpoints para evitar fugas de campos (hashes, tokens, rutas de disco) y estabilizar el contrato."*
- **2.3 — Migraciones en vez de `ALTER TABLE` en runtime.** `database_cloud.py:34-61` ejecuta `ALTER TABLE ... ADD COLUMN` en cada arranque con `except: pass`. Es frágil y oculta errores. *Prompt: "Mueve todo cambio de esquema a migraciones Alembic (ya existe `alembic.ini` y `migrations/`). Elimina los ALTER en `init_cloud_db` y los `except: pass` que tragan errores."*
- **2.4 — Manejo de errores sin tragar excepciones.** El `except Exception: pass` de `config.py:79` y `database_cloud.py:59` enmascara fallos de configuración. *Prompt: "Reemplaza los `except: pass` silenciosos por logging con nivel y re-raise donde el fallo sea de arranque."*
- **2.5 — Trabajo en segundo plano robusto.** El `telegram_listener` se lanza con `asyncio.create_task` en `lifespan` (`main.py:41`); si falla, el `except` global solo loguea. *Prompt: "Aísla los background tasks con supervisión/reintentos y health-check; que un fallo del listener no deje el estado a medias."*
- **2.6 — Reproducibilidad de dependencias.** `requirements.txt` mezcla versiones fijadas y sin fijar (`requests`, `alembic`, `beautifulsoup4`, `xlsxwriter`, `python-dotenv` sin versión). *Prompt: "Fija todas las versiones y migra a `pyproject.toml` + lockfile (uv/pip-tools). Corre `pip-audit` y actualiza lo vulnerable."*

---

## FASE 3 · Reestructuración del frontend (arquitectura)

> Aquí está el "baño de cara" estructural. El objetivo es romper los monolitos y establecer navegación real, lo que a su vez habilita el rendimiento de la Fase 4.

- **3.1 — 🔴 Router real en lugar de `activeTab` + keep-alive.** Hoy `App.tsx:298-395` mantiene **todas las secciones visitadas montadas** a la vez con `className="hidden"` (`visitedTabs`). Cada sección visitada sigue viva: sus `useQuery`/`useInfiniteQuery`, timers y listeners siguen en memoria. Con Catalog/Collection/Purgatory abiertos, hay miles de nodos ocultos y consultas activas simultáneas. *Prompt: "Introduce `react-router-dom` con rutas reales (`/dashboard`, `/catalog`, `/collection`, …). Cada ruta monta y desmonta su página. Sustituye el patrón `visitedTabs`/`hidden`. Usa `<Suspense>` por ruta con el `PowerSwordLoader` como fallback (ya existe el lazy-loading en `App.tsx:14-22`)."*
- **3.2 — 🔴 Trocear los monolitos.** `Config.tsx` (3072 líneas), `Purgatory.tsx` (2253), `Catalog.tsx` (1965), `Collection.tsx` (874), `Dashboard.tsx` (860). Estos ficheros son difíciles de mantener y penalizan el bundle. *Prompt: "Descompón `Config.tsx` en subcomponentes por sección (perfil, imágenes, scrapers, sistema, integraciones) y hooks (`useUserSettings`, etc.). Igual para `Purgatory` y `Catalog`: extrae tarjetas, modales, barras de filtro y la lógica de datos a hooks reutilizables. Meta: ningún componente > ~400 líneas."*
- **3.3 — Autenticación no confiable en cliente.** Todo el gating vive en `localStorage` (`is_logged_in`, `is_sovereign`, `active_user_id` — `App.tsx:32-34`). Es UX, no seguridad (la seguridad real la da la Fase 1). *Prompt: "Deja claro que el gating de cliente es solo UX. Guarda el JWT de forma segura y añade un interceptor axios que, ante 401, limpie sesión y redirija a login. Elimina `active_user_id` como fuente de verdad de identidad."*
- **3.4 — Cliente HTTP unificado.** Hoy cada archivo `api/*.ts` crea su propio axios con headers duplicados y la API key repetida. *Prompt: "Crea `src/api/client.ts` con una única instancia axios: baseURL, interceptor de `Authorization`, manejo global de errores y de 401. Todos los `api/*.ts` la importan."*
- **3.5 — Limpieza de assets duplicados.** En `src/assets` conviven `.png` + `.webp` + versiones `old.*` (`old.Entrance_prod.png`, `old.bg-heman (2).png`, `olldHemanGlassmorphSword.png`…). *Prompt: "Elimina los `old.*` y los `.png` cuando exista `.webp` equivalente ya referenciado. Confirma referencias con grep antes de borrar."*

---

## FASE 4 · Rendimiento de carga entre secciones (el corazón del pedido)

> Objetivo declarado del usuario: **carga fluida entre secciones y valor AAA**. Métricas objetivo: LCP < 2.5 s, bundle inicial < 250 KB gzip, transición entre secciones < 200 ms percibidos.

### 4.1 — 🔴 Code-splitting real de vendors
- **Evidencia:** `dist/assets/index-*.js` = **1.23 MB en un solo chunk**; `dist` total = 18 MB. `recharts` y `framer-motion` (pesados) van al bundle principal. `vite.config.ts` no define `build.rollupOptions.manualChunks`.
- **Acción (prompt):** *"En `vite.config.ts` añade `manualChunks` separando `react/react-dom`, `recharts`, `framer-motion`, `@tanstack/react-query` y `lucide-react` en chunks vendor cacheables. Verifica que el lazy-loading de páginas produce un chunk por página (hoy solo se ve un `index` grande → confirma que el split funciona tras la Fase 3.1). Meta: chunk inicial < 250 KB gzip."*

### 4.2 — 🔴 Optimización de imágenes (17 MB de PNG)
- **Evidencia:** `src/assets` contiene **17.1 MB de PNG**; muchos con `.webp` al lado pero el `.png` sigue empaquetándose, más fondos a resolución completa (`bg-heman.png`, `Entrance_prod.png`).
- **Acción (prompt):** *"Sirve solo `.webp`/`.avif`. Genera variantes responsive (`srcset`) para fondos y héroes. Añade `loading=\"lazy\"` y `decoding=\"async\"` a imágenes de catálogo. Considera `vite-plugin-image-optimizer`. Elimina PNGs redundantes tras verificar referencias. Meta: reducir peso de imágenes iniciales > 80%."*

### 4.3 — Consultas que no se desmontan
- **Evidencia:** con el keep-alive de la Fase 3.1, todas las páginas visitadas mantienen sus queries activas. Además `main.tsx` tiene `staleTime` 5 min y `gcTime` 10 min globales; combinado con montaje permanente = memoria y red innecesarias.
- **Acción (prompt):** *"Tras migrar a router real (3.1), las queries se desmontan solas. Revisa `staleTime`/`gcTime` por tipo de dato (catálogo puede ser más largo; dashboard más corto). Usa `placeholderData: keepPreviousData` en paginación para transiciones sin parpadeo."*

### 4.4 — Prefetch inteligente en hover
- **Acción (prompt):** *"Al hacer hover sobre un ítem del Sidebar, dispara `queryClient.prefetchQuery` de esa sección y `import()` del chunk lazy. Así la sección ya está lista al hacer clic → transición < 200 ms."*

### 4.5 — Virtualización de listas largas
- **Evidencia:** `Catalog.tsx` usa `useInfiniteQuery` (bien) pero renderiza todas las tarjetas acumuladas en el DOM.
- **Acción (prompt):** *"Introduce virtualización (`@tanstack/react-virtual`) en las rejillas de Catálogo/Colección/Purgatorio para que el DOM solo contenga las tarjetas visibles. Crítico con colecciones grandes."*

### 4.6 — Caché de estáticos en nginx
- **Evidencia:** `nginx.conf` tiene gzip pero **no** cabeceras `Cache-Control`/`immutable` para los assets con hash de Vite.
- **Acción (prompt):** *"Añade en nginx `location ~* \\.(js|css|woff2|webp|avif|png)$ { expires 1y; add_header Cache-Control \"public, immutable\"; }`. Los assets de Vite ya llevan hash → seguro cachear un año. Añade `brotli` si el módulo está disponible."*

### 4.7 — Background caching menos agresivo
- **Evidencia:** `App.tsx:117-169` descarga TODO el catálogo de imágenes en segundo plano (1 cada 1.5 s) tras login. Útil pero puede competir con la carga inicial.
- **Acción (prompt):** *"Convierte el pre-cacheo en un Service Worker con estrategia stale-while-revalidate en vez de un bucle en el hilo principal; respeta `navigator.connection.saveData` y arranca solo tras `requestIdleCallback`."*

---

## FASE 5 · Diseño, UX y accesibilidad (pulido AAA)

> El nivel "AAA" en la web también significa **accesibilidad**. Aquí se convierte una app bonita en una app pulida y accesible.

- **5.1 — Accesibilidad (WCAG).** *Prompt: "Audita con axe/Lighthouse: contraste de texto sobre glassmorphism (los `text-white` sobre fondos translúcidos suelen fallar AA), foco visible en todos los interactivos, roles/aria en modales (`CollectionItemDetailModal`, `QuickPreviewModal`, `MarketIntelligenceModal`), navegación por teclado y `aria-label` en botones-icono de `lucide-react`. Objetivo Lighthouse Accessibility ≥ 95."*
- **5.2 — Estados de carga y error coherentes.** Ya existe `PowerSwordLoader` y `ErrorBoundary` (bien). *Prompt: "Estandariza skeletons por sección (no spinner a pantalla completa entre tabs) para que la transición sea percibida como instantánea. Asegura que cada `useQuery` renderiza estado de error accionable."*
- **5.3 — `prefers-reduced-motion`.** framer-motion está muy presente. *Prompt: "Respeta `prefers-reduced-motion` desactivando animaciones no esenciales; mejora rendimiento y accesibilidad."*
- **5.4 — Sistema de diseño / tokens.** *Prompt: "Consolida colores, sombras y radios de glassmorphism en tokens de Tailwind (`theme.extend`) y componentes UI reutilizables (Button, Card, Modal) para eliminar estilos ad-hoc repetidos en los monolitos."*
- **5.5 — Responsive y móvil.** *Prompt: "Verifica los breakpoints en Catálogo/Config (rejillas densas) en 360 px; confirma áreas táctiles ≥ 44 px y que el menú móvil (`isMobileMenuOpen`) atrapa foco."*
- **5.6 — SEO/meta.** `index.html` tiene `lang=\"en\"` pese a ser app en español, sin meta description/OG. *Prompt: "Corrige `lang=\"es\"`, añade meta description y Open Graph para la vista pública `/santuario/:username` (Showcase)."*

---

## FASE 6 · Datos y base de datos

- **6.1 — Índices.** *Prompt: "Revisa consultas de `collection.py`/`products.py` y añade índices en `product_id`, `user_id`, y campos de filtro/orden usados por el catálogo (nombre, fecha de adición, is_vintage). Mide con `EXPLAIN`."*
- **6.2 — Paridad SQLite/Postgres.** El código bifurca dialecto en runtime (`database_cloud.py`). *Prompt: "Documenta y testea la ruta Postgres (prod) como fuente de verdad; usa SQLite solo para tests con las mismas migraciones Alembic."*
- **6.3 — Higiene del repo.** Hay `oraculo.db`, `oraculo.db-shm`, `oraculo.db-wal`, `local_collection_dump.json` y `backups/` en el árbol. *Prompt: "Confirma que artefactos de BD y dumps están en `.gitignore` y no versionados (riesgo de fuga de datos personales de la colección)."*

---

## FASE 7 · Observabilidad, testing y CI/CD

- **7.1 — Tests.** Existe `tests/` y pytest. *Prompt: "Añade tests de integración de autorización (cada endpoint sensible rechaza sin token/rol), tests de los servicios de valuación/matching, y un par de tests e2e de frontend (Playwright ya está en deps) para los flujos login → catálogo → colección."*
- **7.2 — CI.** Los commits recientes muestran auto-sync a Excel vía CI. *Prompt: "Añade a CI: `npm run build` + `lint` + `tsc`, `pytest`, `pip-audit` y `npm audit`, con fallo si el bundle inicial supera el presupuesto (bundlesize budget)."*
- **7.3 — Logging.** loguru ya está bien usado. *Prompt: "Asegura que ningún log imprime secretos ni PII; añade IDs de correlación por request."*

---

## FASE 8 · Verificación final AAA (criterios de aceptación)

Se considera alcanzado el objetivo "Triple-A" cuando:

- ✅ **Seguridad:** `/security-review` sin hallazgos críticos/altos; sin secretos en el bundle; todos los endpoints de datos exigen auth+rol; CORS restringido; cabeceras de seguridad presentes.
- ✅ **Rendimiento:** Lighthouse Performance ≥ 90 en `dashboard`/`catalog`; bundle inicial < 250 KB gzip; LCP < 2.5 s; transición entre secciones < 200 ms percibidos; imágenes iniciales reducidas > 80%.
- ✅ **Accesibilidad:** Lighthouse Accessibility ≥ 95; navegación completa por teclado; `prefers-reduced-motion` respetado.
- ✅ **Mantenibilidad:** ningún componente > ~400 líneas; router real; cliente API único; migraciones Alembic (sin ALTER en runtime); dependencias fijadas.
- ✅ **Calidad:** CI en verde con tests de autorización y presupuesto de bundle.

---

## Orden recomendado de ejecución (resumen)

```
FASE 0  Línea base + rama + rotar secretos        (0.5 día)
FASE 1  Seguridad crítica  ← BLOQUEANTE           (2-3 días)   ⟵ empezar SÍ o SÍ aquí
FASE 2  Backend hardening + Alembic + contrato     (2 días)
FASE 3  Router real + trocear monolitos            (3-4 días)   ⟵ habilita la Fase 4
FASE 4  Rendimiento: chunks, imágenes, virtual.    (2-3 días)   ⟵ el "baño de cara"
FASE 5  Accesibilidad + diseño AAA                 (2 días)
FASE 6  Índices + datos                            (1 día)
FASE 7  Tests + CI + observabilidad                (2 días)
FASE 8  Verificación contra criterios AAA          (0.5 día)
```

> **Regla de oro:** la Fase 1 no se pospone. El resto puede solaparse, pero 3 debe ir antes que 4 (el router habilita el split y el desmontaje de queries).
