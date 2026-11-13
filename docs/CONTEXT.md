# Contexto de Dominio y Arquitectura — Oráculo de Nueva Eternia

Este documento define el glosario operativo, las fronteras de persistencia y los invariantes de seguridad consensuados bajo la metodología **Organic Driven Development (ODD — Gentle AI v4)**.

---

## 1. Glosario del Dominio

* **Catálogo Maestro (`products`, `vintage_products`):** Fuente canónica de figuras de *Masters of the Universe* (líneas Nueva Eternia / Origins y reliquias Vintage).
* **Oferta Validada (`offers`) vs. Purgatorio (`pending_matches`):**
  * **Purgatorio (`pending_matches`):** Zona de cuarentena obligatoria (*Purgatory-First Policy*) donde aterrizan los hallazgos de los scrapers antes de vincularse a un producto canónico.
  * **Oferta (`offers`):** Anuncio comercial o P2P ya vinculado y validado contra una figura del catálogo, alimentando series históricas (`price_history`, `product_monthly_stats`).
  * **Lista Negra (`blackcluded_items`):** URLs descartadas explícitamente para impedir su re-ingesta en futuras incursiones.
* **Fortaleza / Colección Personal (`collection_items`):** Inventario privado por usuario (`owner_id`), incluyendo estado de conservación (`condition`, `grading`) e inversión privada (`purchase_price`, protegida por modo incógnito).
* **Escudo de Eternia (`authorized_devices`):** Registro de huellas de dispositivos autorizados (`device_id`) para operaciones protegidas.
* **Grimorio Lore (`character_lore`, `product_lore`):** Enciclopedia canónica de biografías, facciones y atributos RPG para cartas coleccionables.

---

## 2. Arquitectura de Persistencia Híbrida e Invariantes de Seguridad

1. **Paridad Dual (`SQLite` + `Supabase PostgreSQL`):**
   * En desarrollo/offline y tests herméticos (`pytest`), el sistema opera sobre SQLite (`oraculo.db` / `:memory:`) en el esquema por defecto.
   * En producción y pipelines cloud (`GitHub Actions`), la fuente de verdad reside en **Supabase (PostgreSQL)** conectada directamente desde el backend mediante `SUPABASE_DATABASE_URL` (`SessionCloud`).
2. **Aislamiento Total de la Data API Pública (`PostgREST` / `GraphQL`):**
   * El cliente React (`frontend/`) **jamás** se conecta directamente a PostgREST (`/rest/v1/`) ni utiliza claves `anon` en el navegador; consume exclusivamente la API de FastAPI (`/api/...`) y las URLs públicas de imágenes del servicio independiente **Supabase Storage** (`/storage/v1/object/public/motu-catalog/`).
   * Por tanto, el esquema `public` de PostgreSQL debe permanecer **100 % cerrado** para los roles `anon` y `authenticated` (`REVOKE ALL`, `ALTER DEFAULT PRIVILEGES` y desactivación de `public` en *Exposed Schemas* de Data API).
3. **Invariante Zero-Trust de Row-Level Security (RLS):**
   * **Ninguna tabla propia en `public`** (incluidas tablas técnicas como `alembic_version`) puede existir con `relrowsecurity = false`.
   * La base de datos se autoprotege mediante el `EVENT TRIGGER` `ensure_rls_on_public` (`ON ddl_command_end`), que habilita RLS y revoca privilegios públicos en la misma transacción de cualquier `CREATE TABLE`.
4. **Autoridad Única de Esquema (Alembic):**
   * Queda prohibido mutar el esquema de producción desde servicios de aplicación (`NexusService`, `NexusVintageService`) mediante `universal_migrator.py` o añadir sentencias DDL (`ALTER TABLE` / `ENABLE ROW LEVEL SECURITY`) en el arranque de FastAPI (`init_cloud_db`), evitando bloqueos `ACCESS EXCLUSIVE LOCK` sobre el pooler transaccional (`:6543`) y estados `fail-open`.
   * Toda evolución de esquema debe versionarse en `migrations/versions/` de forma idempotente y validarse mecánicamente en CI (`tests/unit/test_api_db_rls_governance.py`).
