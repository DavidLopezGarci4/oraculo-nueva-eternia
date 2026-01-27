# 🗺️ Architecture Map: Oráculo Nueva Eternia (3OX vec3 Audit)

Este mapa detalla la estructura actual del proyecto bajo el estándar **3OX Tier 3**.

## 1. 🧠 Núcleo de Control (Core 3OX)
Archivos fundamentales que rigen el comportamiento del agente y el sistema.

| Archivo | Estado | Propósito |
| :--- | :--- | :--- |
| `sparkfile.md` | ✅ Activo | Especificación maestra y directivas core. |
| `brain.rs` | ✅ Activo | Configuración lógica de bajo nivel (Rust). |
| `tools.yml` | ✅ Activo | Registro de herramientas disponibles. |
| `routes.json` | ✅ Activo | Mapa de enrutamiento operativo. |
| `limits.json` | ✅ Activo | Límites de recursos y seguridad. |
| `run.rb` | ✅ Activo | Coordinador del entorno de ejecución. |
| `3ox.log` | ✅ Activo | Diario de actividad bajo estándar Sirius. |

## 2. 🛡️ Superficies Protegidas (vec3/)
Estructura de aislamiento para reglas, librerías y estado.

- **vec3/rc/**: Reglas inmutables y definiciones de sistema.
- **vec3/lib/**: Librerías estáticas de referencia.
- **vec3/dev/**: Adaptadores e I/O Bridges (en desarrollo).
- **vec3/var/**: Estado dinámico, recibos de operaciones y persistencia temporal.

## 3. 🏗️ Capas de Aplicación (src/)
Implementación de lógica de negocio siguiendo **Clean Architecture**.

- **domain/**: Entidades MOTU, reglas de negocio puras.
- **application/**: Casos de uso, servicios (`Nexus`, `Sentinel`, `Logistics`).
- **infrastructure/**: Implementaciones técnicas (Supabase, Scrapers, Migraciones).
- **interfaces/**: Puerta de enlace API (FastAPI) y esquemas Pydantic.
- **core/**: Utilidades transversales (Logger, Config, Audit).

## 4. ⚠️ Auditoría de Cumplimiento vec3 (Deuda Técnica)

### 🔴 Archivos No Conformes (Fuera de Jerarquía)
Los siguientes archivos viven en la raíz y rompen el protocolo 3OX. Deberían ser movidos a `/scripts` o `/src/application/jobs`.

1.  **Scripts de Debug/Prueba**:
    - `audit_ebay_html.py`, `audit_wallapop_fields.py`, `debug_wallapop_curl.py`, `get_wallapop_urls.py`.
2.  **Utilidades de Sistema**:
    - `backup_db.ps1`, `launch_eternia.ps1`, `run_daily_scan.bat`.
3.  **Archivos de Migración/Carga**:
    - `bulk_stat_sync.py`, `migrate_dna.py`, `sync_to_cloud.py`.

### 🟢 Archivos Conformes
- Todos los componentes dentro de `src/` respetan la segregación de capas.
- El kernel 3OX está correctamente configurado en la raíz.

---

## 🚀 Recomendación de Refactorización
Mover los +50 scripts de la raíz a una estructura jerárquica:
- `/scripts/debug/`: Para análisis manuales de HTML/Selectors.
- `/scripts/ops/`: Para automatizaciones de backups y despliegues.
- `/src/application/jobs/`: Para ejecuciones recurrentes de datos.
