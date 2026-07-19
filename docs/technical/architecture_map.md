# Architecture Map: Nueva Eternia (3OX vec3 Audit)

> [!NOTE]
> Este archivo es un mapa físico de directorios. Para explicaciones detalladas del stack tecnológico, conexiones entre capas y flujos de datos, dirígete a la **[DOCUMENTACION MAESTRA](DOCUMENTACION_MAESTRA.md)**.

Este mapa detalla la estructura actual del proyecto bajo el estándar **3OX Tier 3**.

## 1. Núcleo de Control (Core 3OX)

Archivos fundamentales que rigen el comportamiento del agente y el sistema.

| Archivo | Estado | Propósito |
| :--- | :--- | :--- |
| `3ox.log` | Activo | Diario de actividad bajo estándar Sirius. |
| `brain.rs` | Activo | Configuración lógica de bajo nivel (Simulado/Rust). |
| `Dockerfile` | Activo | Definición del contenedor para despliegue industrial. |
| `docker-compose.yml` | Activo | Orquestación de servicios (API, Web, DB). |
| `launch_ark.ps1` | Activo | Script maestro de lanzamiento (Modo Arca). |
| `sparkfile.md` | Activo | Especificación maestra y directivas core. |

## 2. Superficies Protegidas (vec3/)

Estructura de aislamiento para reglas, librerías y estado.

- **vec3/rc/**: Reglas inmutables y definiciones de sistema.
- **vec3/lib/**: Librerías estáticas de referencia.
- **vec3/dev/adapters/**: Adaptadores de runtime forzados (UTF-8, etc.).
- **vec3/var/**: Estado dinámico, recibos de operaciones y persistencia temporal.

## 3. Capas de Aplicación (src/)

Implementación de lógica de negocio siguiendo **Clean Architecture**.

- **domain/**: Entidades MOTU (`ProductModel`, `OfferModel`), reglas de negocio puras.
- **application/services/**: Servicios maestros (`Nexus`, `Sentinel`, `Logistics`, `DealScorer`).
- **application/jobs/**: Tareas programadas (`daily_scan.py`).
- **infrastructure/scrapers/**: Motores de incursión (Playwright, BeautifulSoup).
- **infrastructure/database/**: Repositorios y sesión de base de datos (Supabase/PostgreSQL).
- **infrastructure/services/**: Adaptadores de servicios externos (`telegram_service.py` para despacho de alertas y telemetría, `telegram_listener.py` para escucha asíncrona de comandos mediante Long Polling).
- **interfaces/api/**: Puerta de enlace API (FastAPI). Estructura modular completa:
  - `main.py` — startup con lifespan context manager, CORS, `include_router` únicamente.
  - `deps.py` — dependencias FastAPI: `verify_api_key`, `verify_device`, `ensure_scrapers_registered`, `get_current_user`, `create_access_token`.
  - `schemas.py` — modelos Pydantic centralizados (21 schemas, incluye `Token`).
  - `routers/health.py` — `/api/health`.
  - `routers/auth.py` — `/api/auth/*` (login, register, reset-password). Login devuelve `access_token` JWT.
  - `routers/scrapers.py` — `/api/scrapers/*` (status, logs, run, stop) + `run_scraper_task`.
  - `routers/admin.py` — `/api/admin/*` (users CRUD, devices, nexus sync, anomaly, reset-smartmatches).
  - `routers/products.py` — `/api/products/*`, `/api/auctions/*`, `/api/market/*`, `/api/intelligence/*`, `/api/wallapop/preview`, `/api/vintage/miscellaneous`.
  - `routers/collection.py` — `/api/collection/*`, `/api/guardian/export/*`.
  - `routers/purgatory.py` — `/api/purgatory/*`, `/api/offers/*/unlink|relink`, `/api/purgatory/{pending_id}/miscellaneous`, `/api/vintage/miscellaneous/revert/{item_id}`, `DELETE /api/vintage/miscellaneous/{item_id}`.
  - `routers/dashboard.py` — `/api/dashboard/*`.
  - `routers/users.py` — `/api/users/*` (settings, location), `/api/wallapop/import`, `/api/radar/p2p-opportunities`.
  - `routers/system.py` — `/api/system/audit`.
  - `routers/vault.py` — `/api/vault/*`, `/api/excel/sync`, `/api/vault/download-images/*`.
  - Mount `/api/static/images` — montura de StaticFiles para servir imágenes locales desde data/image_cache.
  - `routers/logistics.py` — `/api/logistics/calculate-cart`.
- **core/**: Utilidades transversales (Logger, Config, Audit, SecurityShield).
  - `config.py` — incluye `JWT_SECRET` y `JWT_EXPIRE_MINUTES` (Phase 59).

## 4. Interfaz de Usuario (frontend/)

Ecosistema moderno en React.

- **src/pages/**: Vistas principales (`Dashboard`, `Catalog`, `Fortress`, `Purgatory`, `VintageMiscellaneous`).
- **src/components/**: Componentes atómicos y tácticos (`ItemCard`, `ScraperLogs`).
- **src/api/**: Clientes para la comunicación con el FastAPI Broker.
- **App.tsx**: Nodo maestro de estado y gestión reactiva de identidad (User State Lifting).

---

## 5. Scripts de Operaciones (scripts/)

Organización por propósito para mantener la raíz limpia:

| Carpeta | Contenido |
| :--- | :--- |
| `scripts/diagnostics/` | Lectura de estado: `check_*`, `diagnose_*`, `cloud_db_check`, etc. |
| `scripts/audits/` | Validación e informes: `audit_*`, `verify_*`. |
| `scripts/maintenance/` | Operaciones de escritura: `fix_*`, `repair_*`, `init_*`, `sync_*`, `migrate_*`. |
| `scripts/experimental/` | Scripts exploratorios y reproductores one-shot. |
| `scripts/smoke/` | Pruebas de humo contra la API en vivo (`smoke_*.py`). Requieren `ORACULO_API_KEY` en env. |
| `scripts/` (raíz) | Scripts de uso frecuente consolidados previamente (cleanup, migration, cloud). |

## 6. Gestión Global de Errores

`main.py` registra dos handlers centralizados que estandarizan el formato de error en toda la API:

| Handler | Trigger | Response |
| :--- | :--- | :--- |
| `RequestValidationError` | Cuerpo/parámetros inválidos (422) | `{status, type: "validation_error", detail: [...]}` |
| `Exception` | Excepción no capturada (500) | `{status, type: "server_error", detail: "Internal server error"}` |

Las `HTTPException` existentes siguen retornando `{"detail": "..."}` con el handler por defecto de FastAPI (compatibilidad con el frontend).

---

## 7. Endpoints sin consumer en el frontend

Audit realizado sobre `frontend/src/api/`. Los siguientes endpoints tienen implementación backend pero no tienen llamada en el frontend actual:

| Endpoint | Motivo probable |
| :--- | :--- |
| `POST /api/admin/users/create` | Panel de admin pendiente |
| `GET /api/admin/devices` | Panel de gestión de dispositivos pendiente |
| `POST /api/admin/devices/{id}/authorize` | Ídem |
| `DELETE /api/admin/devices/{id}` | Ídem |
| `POST /api/admin/validate-anomaly` | Acción de Purgatorio pendiente |
| `GET /api/auctions/products` | Página de subastas no implementada |
| `GET /api/intelligence/market/{id}` | Vista de inteligencia de mercado pendiente |
| `GET /api/wallapop/preview` | Puente Wallapop (bridge, uso interno) |
| `POST /api/vault/stage` | Flujo de importación de bóveda pendiente |
| `GET /api/market/analytics/{id}` | Vista de analítica pendiente |
| `GET /api/health` | Endpoint de monitorización (no necesita UI) |
| `GET /api/system/audit` | Herramienta de admin (acceso directo) |
| `GET /api/auth/users` | Legacy, sólo para debugging |

---

## 8. Tests (tests/)

Suite de tests unitarios y de integración ejecutada con **pytest**:

| Archivo | Cobertura / Tipo | Propósito |
| :--- | :--- | :--- |
| `tests/conftest.py` | Configuración Global | Fixture sesión: SQLite in-memory (StaticPool), TestClient, usuarios de prueba. |
| `tests/integration/test_api_auth.py` | Integración (API) | Register, login, JWT token, `get_current_user` con Bearer. |
| `tests/integration/test_api_errors.py` | Integración (API) | Validation error handler (422), HTTPException pass-through (403/404). |
| `tests/integration/test_api_health.py` | Integración (API) | `/api/health`, OpenAPI schema disponible. |
| `tests/integration/test_api_permissions.py` | Integración (API) | API key guard, device guard, endpoints públicos, dashboard stats. |
| `tests/integration/test_api_showcase.py` | Integración (API) | Control de acceso y privacidad del Santuario (showcase público). |
| `tests/integration/test_api_image_cache.py` | Integración (API) | Endpoints de descarga, estado y cancelación del caché local de imágenes. |
| `tests/integration/test_phase0_migration.py` | Integración (DB) | Migraciones de base de datos e integridad estructural. |
| `tests/unit/test_api_motu_relevance.py` | Unitario (Core) | Filtros de relevancia y descarte heurístico para figuras clásicas MOTU. |
| `tests/unit/test_api_telegram_alerts.py` | Unitario (Alertas) | Envío y coincidencia de alertas multi-usuario (Wishlist, precios, vintage). |
| `tests/unit/test_matcher_precision.py` | Unitario (Matching) | Precisión de tokens y emparejamiento semántico del vinculador. |
| `tests/unit/test_specific_purgatory_cases.py` | Unitario (Matching) | Casos extremos y resoluciones conflictivas en Purgatorio. |

Ejecutar: `.venv\Scripts\python -m pytest` (33 tests, 0 fallos)

---

## Notas de Auditoría

- El proyecto ha sido consolidado eliminando el legado de Streamlit.
- La raíz quedó limpia tras mover 49 scripts a `scripts/{diagnostics,audits,maintenance,experimental,smoke}/`.
- `oraculo.db.bak` y `*.db.bak` excluidos del tracking de git (`.gitignore`).
- **Phase 55**: Restauración del Legado y Motor de Graduación Avanzada (ASTM/C).
- **Phase 56**: Blindaje de conexión BD (`pool_pre_ping`, `pool_recycle`), cancelación cooperativa de scrapers (`threading.Event`), eliminación de usuarios, diagnóstico SMTP y optimización de intervalos de refresco frontend.
- **Phase 57**: Refactorización Visual UX & Búsqueda Flexible.
- **Phase 58**: Reestructuración — API modularizada en 9 routers, raíz limpia, secretos en env, `main.py` de 2485 → 55 líneas.
- **Phase 59**: Autenticación JWT (`PyJWT`, `create_access_token`, `get_current_user`), tests de integración con SQLite in-memory (21 tests, 0 fallos).
- **Phase 60**: Split de `misc.py` en 4 routers semánticos (`users`, `system`, `vault`, `logistics`). Optimización de `/api/purgatory`: índice invertido por token reduce el matching de O(pending × products) a O(pending × candidatos), ~10-50x más rápido.
- **Phase 61**: Global exception handler centralizado en `main.py` (ValidationError → 422 estructurado, Exception → 500 limpio). Audit de endpoints sin consumer frontend documentado (13 endpoints identificados). 25 tests de integración, 0 fallos.
- **Phase 62**: Hardening de compatibilidad Python 3.12+:
  - `datetime.utcnow()` reemplazado por `datetime.now(timezone.utc)` en todos los modelos y routers (12 puntos de corrección).
  - `DISTINCT ON` eliminado de `products.py` (incompatible con SQLite/futuras versiones de SQLAlchemy); deduplicación movida a Python con `seen` set.
  - pytest configurado en `pyproject.toml` (`testpaths = ["tests"]`, `python_files = ["test_api_*.py"]`) — aísla suite API de scripts heredados.
  - Alerta de `JWT_SECRET` inseguro en arranque (`logger.critical` si se usa el valor por defecto).
  - 25 tests de integración, 0 fallos, 0 warnings de deprecación.
- **Phase 63**: Segregación Estricta de Catálogos (Eternia Vintage vs Nueva Eternia) y Ordenación Dinámica por Purgatorio:
  - Reclasificadas figuras de Origins erróneamente en Vintage (Skeletor Vintage Sculpt y 200x) a is_vintage = False y migradas sus existencias a la Fortaleza de Nueva Eternia.
  - Corregido el bug de auto-promoción a vintage en match_purgatory respetando estrictamente product.is_vintage.
  - Segregación estricta de Drawer y Modal en Purgatorio.tsx con sugerencias vintage inteligentes (vintageOracleSuggestions).
  - Implementación de conteo en memoria optimizado con token index (get_purgatory_counts) para inyectar purgatory_match_count en API de productos.
  - Ordenación jerárquica en Eternia Vintage: 1º prioridad de ofertas activas, 2º cantidad de ofertas pendientes en Purgatorio (descendente), y 3º fallback por ID de base de datos (ascendente).
- **Phase 64**: Miscelánea Vintage, Rediseño de Métricas y Manual de Usuario (03/06/2026):
  - Añadido modelo `VintageMiscellaneousModel` y endpoints de desvío a Miscelánea, listado y reversión en el backend.
  - Creada página `VintageMiscellaneous.tsx` con listado de lotes e integración de reversión.
  - Rediseñados botones del modal de colección para ser simétricos e integrada la guía interactiva desplegable de la escala C de conservación.
  - Creadas 8 guías de usuario estructuradas e independientes en la carpeta `docs/manual_usuario/`.
- **Phase 65**: Características Pareto 80/20 y Blindaje Wallapop (07/06/2026):
  - Santuario Compartido (Showcase) público exento de costes financieros en `/santuario/:username`.
  - Filtro Cruzado de Deseos ("Solo Deseos") en Mercader de Eternos.
  - Completitud por subcategorías (Waves) y Arsenal Analytics (gráfico circular de conservación) en Orbe de Grayskull.
  - Script `renew_ssl.sh` local con Certbot Docker y recarga de Nginx.
  - Scraper Wallapop híbrido con peticiones directas API via `curl_cffi` (impersonación de TLS de Chrome) y Playwright de respaldo.
  - Corrección del calibrador de carga de Skeletor: reemplazo de báculo por la silueta de Skeletor Vintage y la espada real (`GlassmorphSword.png`), alineación vertical centrada horizontalmente a 125, y migración a `skeletor_sword_coords`.
  - Integración de calibración para He-Man Moderno: mapeo del calibrador y loader en la pantalla de carga predeterminada (`HemanGlassmorphSword.png`) usando la clave `modern_sword_coords` en localStorage para reflejar las coordenadas en toda la app.
- **Phase 66**: Bot Bidireccional de Telegram, Alertas Multi-usuario y Telemetría de Auditoría (08/06/2026):
  - Añadida columna `telegram_chat_id` en la tabla `users` con rutinas de migración automática en `database_cloud.py` y `universal_migrator.py`.
  - Diseñado e integrado un receptor asíncrono de comandos (`telegram_listener.py`) en segundo plano que procesa comandos con autorización según rol.
  - Desarrollado un motor de despacho de alertas multi-usuario (`check_and_send_multiuser_alerts` en `pipeline.py`) cruzando ofertas con listas de deseos y precio de múltiples Guardianes.
  - Habilitada telemetría atómica en `data/telegram_telemetry.json` y redactado documento de auditoría de flujo y datos en `docs/AUDITORIA_TELEGRAM.md`.

---


- **Phase 67**: Optimización Extrema, Bypass de proxies en Amazon y Trazabilidad Operativa (09/06/2026):
  - Implementación de Lazy Keep-Alive en `App.tsx` para persistencia en memoria de pestañas y aceleración de transiciones a 0ms.
  - Refactorización de inputs de inversión en `CollectionItemDetailModal.tsx` (vacíos por defecto) y badges de compra en `Collection.tsx`.
  - Configuración de ScraperAPI con proxies residenciales en España (`premium=true`, `country_code=es`) para eludir bloqueos WAF en Amazon.es.
  - Sanitización robusta de comillas en la cadena de conexión de `database_cloud.py`.
  - Reducción de workers de Uvicorn a 1 en contenedores de producción para eliminar colisiones del receptor de Telegram.
  - Corrección de advertencias Node.js 20 en GitHub Actions (`ci.yml`).

- **Phase 68**: Caché Local de Imágenes y Fallback Híbrido (09/06/2026):
  - Servidor de estáticos FastAPI en `/api/static/images` apuntando a `data/image_cache`.
  - APIs de descarga de imágenes en lote, estado y cancelación asíncrona segura en `routers/vault.py`.
  - Componente React `MOTUImage` con soporte para toggle `use_local_images` en localStorage y fallback instantáneo a hotlink original en error.
  - Integración de barra de progreso e interruptor en `Config.tsx`.
  - Reemplazo de etiquetas `<img>` estándar por `<MOTUImage>` en Showcase, Collection, Catalog, Vintage y Dashboard.
  - Creación de prueba de integración `test_api_image_cache.py` con cobertura completa del ciclo de vida de la descarga.

- **Phase 72**: Bypass de Amazon, Purgatorio Asíncrono y Resalto de Ofertas (20/06/2026):
  - Integración de renderizado completo JS (`render=true`) en ScraperAPI para Amazon.es y corrección de bloqueos falsos por nombres de figuras robóticas (como Multi-Bot o Roboto).
  - Migración de acciones de Purgatorio a BackgroundTasks en el backend de FastAPI para encolamiento asíncrono con respuesta inmediata (0ms).
  - Implementación de set en memoria `PROCESSING_IDS` en el Purgatorio para ocultación reactiva inmediata en el frontend (prevención de efecto zombie).
  - Intensificación del resplandor de color en las tarjetas de figuras del Catálogo que tengan ofertas activas (celeste para Moderno, dorado para Vintage) sin badges flotantes.
  - Incorporación de filtro de tránsito experimental con switch "On/Off" en el frontend del Purgatorio para separar ofertas de tipo Retail de ofertas P2P (Wallapop/eBay).

- **Phase 81**: Nexo de Fusión Divina, Scroll Infinito y Optimización de Rendimiento Extremo (19/07/2026):
  - Fusión de productos centralizada en Configuración > Inventario, con reasignación y persistencia coherente de is_vintage en ofertas y borrado atómico de ítems duplicados.
  - Ordenación responsiva en Mi Fortaleza por fecha de agregado (`acquired_at`) con selector de 3 columnas de bajo perfil.
  - Reducción del 94% en transferencia de assets mediante conversión y compresión masiva de imágenes a formato WebP.
  - Reducción del JS de arranque del frontend a <200KB mediante Code Splitting estructurado en App.tsx.
  - Paginación de base de datos e Infinite Scroll con Intersection Observer en Catalog.tsx y Collection.tsx.
  - Conmutador manual de rendimiento ("Efectos Clásicos" vs "Activados") para conmutar los cálculos de cursor 3D en la GPU.
  - Índices de rendimiento en base de datos local y recálculo masivo de estadísticas para 519 productos, reactivando el Radar de Oportunidades.

*Última actualización: 2026-07-19 - Phase 81: Nexo de Fusión Divina, Scroll Infinito y Optimización de Rendimiento Extremo.*
