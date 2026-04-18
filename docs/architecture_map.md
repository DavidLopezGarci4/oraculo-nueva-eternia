# 🗺️ Architecture Map: Nueva Eternia (3OX vec3 Audit)

Este mapa detalla la estructura actual del proyecto bajo el estándar **3OX Tier 3**.

## 1. 🧠 Núcleo de Control (Core 3OX)

Archivos fundamentales que rigen el comportamiento del agente y el sistema.

| Archivo | Estado | Propósito |
| :--- | :--- | :--- |
| `3ox.log` | ✅ Activo | Diario de actividad bajo estándar Sirius. |
| `brain.rs` | ✅ Activo | Configuración lógica de bajo nivel (Simulado/Rust). |
| `Dockerfile` | ✅ Activo | Definición del contenedor para despliegue industrial. |
| `docker-compose.yml` | ✅ Activo | Orquestación de servicios (API, Web, DB). |
| `launch_ark.ps1` | ✅ Activo | Script maestro de lanzamiento (Modo Arca). |
| `sparkfile.md` | ✅ Activo | Especificación maestra y directivas core. |

## 2. 🛡️ Superficies Protegidas (vec3/)

Estructura de aislamiento para reglas, librerías y estado.

- **vec3/rc/**: Reglas inmutables y definiciones de sistema.
- **vec3/lib/**: Librerías estáticas de referencia.
- **vec3/dev/adapters/**: Adaptadores de runtime forzados (UTF-8, etc.).
- **vec3/var/**: Estado dinámico, recibos de operaciones y persistencia temporal.

## 3. 🏗️ Capas de Aplicación (src/)

Implementación de lógica de negocio siguiendo **Clean Architecture**.

- **domain/**: Entidades MOTU (`ProductModel`, `OfferModel`), reglas de negocio puras.
- **application/services/**: Servicios maestros (`Nexus`, `Sentinel`, `Logistics`, `DealScorer`).
- **application/jobs/**: Tareas programadas (`daily_scan.py`).
- **infrastructure/scrapers/**: Motores de incursión (Playwright, BeautifulSoup).
- **infrastructure/database/**: Repositorios y sesión de base de datos (Supabase/PostgreSQL).
- **interfaces/api/**: Puerta de enlace API (FastAPI). Estructura modular:
  - `main.py` — startup, CORS, `include_router` únicamente.
  - `deps.py` — dependencias FastAPI: `verify_api_key`, `verify_device`, `ensure_scrapers_registered`.
  - `schemas.py` — modelos Pydantic centralizados (20 schemas).
  - `routers/health.py` — `/api/health`.
  - `routers/auth.py` — `/api/auth/*` (login, register, reset-password).
  - `routers/scrapers.py` — `/api/scrapers/*` (status, logs, run, stop) + `run_scraper_task`.
  - *(pendiente)* `routers/products.py`, `routers/collection.py`, `routers/purgatory.py`, `routers/dashboard.py`, `routers/admin.py`.
- **core/**: Utilidades transversales (Logger, Config, Audit).

## 4. 🌐 Interfaz de Usuario (frontend/)

Ecosistema moderno en React.

- **src/pages/**: Vistas principales (`Dashboard`, `Catalog`, `Fortress`, `Purgatory`).
- **src/components/**: Componentes atómicos y tácticos (`ItemCard`, `ScraperLogs`).
- **src/api/**: Clientes para la comunicación con el FastAPI Broker.
- **App.tsx**: Nodo maestro de estado y gestión reactiva de identidad (User State Lifting).

---

## 5. 🛠️ Scripts de Operaciones (scripts/)

Organización por propósito para mantener la raíz limpia:

| Carpeta | Contenido |
| :--- | :--- |
| `scripts/diagnostics/` | Lectura de estado: `check_*`, `diagnose_*`, `cloud_db_check`, etc. |
| `scripts/audits/` | Validación e informes: `audit_*`, `verify_*`. |
| `scripts/maintenance/` | Operaciones de escritura: `fix_*`, `repair_*`, `init_*`, `sync_*`, `migrate_*`. |
| `scripts/experimental/` | Scripts exploratorios y reproductores one-shot. |
| `scripts/smoke/` | Pruebas de humo contra la API en vivo (`smoke_*.py`). Requieren `ORACULO_API_KEY` en env. |
| `scripts/` (raíz) | Scripts de uso frecuente consolidados previamente (cleanup, migration, cloud). |

---

## 🔎 Notas de Auditoría

- El proyecto ha sido consolidado eliminando el legado de Streamlit.
- La raíz quedó limpia tras mover 49 scripts a `scripts/{diagnostics,audits,maintenance,experimental,smoke}/`.
- `oraculo.db.bak` y `*.db.bak` excluidos del tracking de git (`.gitignore`).
- **Phase 55**: Restauración del Legado y Motor de Graduación Avanzada (ASTM/C).
- **Phase 56**: Blindaje de conexión BD (`pool_pre_ping`, `pool_recycle`), cancelación cooperativa de scrapers (`threading.Event`), eliminación de usuarios, diagnóstico SMTP y optimización de intervalos de refresco frontend.
- **Phase 57**: Refactorización Visual UX & Búsqueda Flexible (Reserva Táctica de loader inmersivo a transiciones primarias e inputs de texto multilinea mobile-first).
- **Phase 58**: Reestructuración — API modularizada en routers, raíz limpia, secretos en env.

---

*Última actualización: 2026-04-18 - Phase 58: Reestructuración de raíz y API modular.*
