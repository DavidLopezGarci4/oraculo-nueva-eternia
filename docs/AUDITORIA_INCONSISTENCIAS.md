# 🔍 Reporte de Auditoría: Inconsistencias y Fallas del Código (Fase 75)

Este log recoge las discrepancias y fallas menores identificadas en la base de código del Oráculo mediante la aplicación de la skill `code-error-analyzer`.

---

## 1. backend / API

### 1.1 Inconsistencias de Registro de Scrapers (deps.py vs scrapers.py)
*   **Detalle**: Los scrapers `Triguetech` y `LaMansionDelTerror` están presentes en `spiders_map` (`routers/scrapers.py`), pero no se encuentran en la lista `spiders_to_check` de la función `ensure_scrapers_registered()` en `deps.py`.
*   **Impacto**: Al inicializar el servidor, estos scrapers no se registrarán automáticamente en la tabla `scraper_status` de la base de datos si no existían previamente.
*   **Scraper Tradeinn Huerfano**: `Tradeinn` está listado en `spiders_to_check` pero comentado en `spiders_map`.

### 1.2 Deprecaciones de fecha/hora en SQLAlchemy Repositories
*   **Detalle**: El repositorio de productos (`src/infrastructure/repositories/product.py` líneas 134 y 138) sigue empleando `datetime.utcnow()` que ha sido depreciado en Python 3.12/3.13.
*   **Impacto**: Genera logs ruidosos de advertencia de deprecación en la ejecución de la suite de pruebas unitarias (`pytest`).
*   **Mitigación**: Reemplazar por `datetime.now(datetime.UTC)` o `datetime.now(timezone.utc)`.

---

## 2. Frontend / TypeScript

### 2.1 Importación Híbrida Dinámica/Estática en Bundling (Vite)
*   **Detalle**: El archivo `src/api/admin.ts` es importado dinámicamente por `Catalog.tsx` y `Collection.tsx`, pero estáticamente por `App.tsx` y `Navbar.tsx`.
*   **Impacto**: Genera una advertencia de Rollup en el build: *`dynamic import will not move module into another chunk`*. Esto inhabilita el code-splitting óptimo para este módulo en producción.

### 2.2 Desajuste del Nombre del Wave en el Frontend
*   **Detalle**: En `Dashboard.tsx` línea 596 se incluye un parche de cadena estático:
    ```typescript
    group.name.toUpperCase() === 'MASTERS OF THE WWE UNIVERSE RIN' ? 'MASTERS OF THE WWE UNIVERSE RING' : group.name
    ```
*   **Impacto**: Acoplamiento rígido de cadenas. El error ortográfico viene originalmente del parseo o del registro en base de datos.
*   **Mitigación**: Corregir el nombre del Wave directamente en la semilla de datos de la base de datos en lugar de parchearlo en tiempo de ejecución en la capa de vista.

---

## 3. Base de Datos / Supabase

### 3.1 Constraints de Clave Foránea en Modo Offline
*   **Detalle**: Cuando el backend opera en modo offline (sin `SUPABASE_DATABASE_URL` activa), interactúa exclusivamente con SQLite `oraculo.db`.
*   **Impacto**: Algunas validaciones complejas de integridad referencial forzadas en PostgreSQL en la nube no se ejecutan localmente si el motor SQLite no tiene activos los PRAGMAs de foreign keys por defecto.

---

*Log generado y auditado mediante la skill local `.agents/skills/code-error-analyzer/`.*
