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
- **interfaces/api/**: Puerta de enlace API (FastAPI) y esquemas Pydantic.
- **core/**: Utilidades transversales (Logger, Config, Audit).

## 4. 🌐 Interfaz de Usuario (frontend/)

Ecosistema moderno en React.

- **src/pages/**: Vistas principales (`Dashboard`, `Catalog`, `Fortress`, `Purgatory`).
- **src/components/**: Componentes atómicos y tácticos (`ItemCard`, `ScraperLogs`).
- **src/api/**: Clientes para la comunicación con el FastAPI Broker.
- **App.tsx**: Nodo maestro de estado y gestión reactiva de identidad (User State Lifting).

---

## 🔎 Notas de Auditoría

- El proyecto ha sido consolidado eliminando el legado de Streamlit.
- Los scripts de la raíz están en proceso de migración hacia `scripts/` o `src/application/jobs/` para mantener la pureza de la raíz.
- **Phase 55**: Restauración del Legado y Motor de Graduación Avanzada (ASTM/C).
- **Phase 56**: Blindaje de conexión BD (`pool_pre_ping`, `pool_recycle`), cancelación cooperativa de scrapers (`threading.Event`), eliminación de usuarios, diagnóstico SMTP y optimización de intervalos de refresco frontend.
- **Phase 57**: Refactorización Visual UX & Búsqueda Flexible (Reserva Táctica de loader inmersivo a transiciones primarias e inputs de texto multilinea mobile-first).

---

*Última actualización: 28/02/2026 - Fase 57: Refactorización Visual UX.*
