# Adopción real de Alembic (Fase AAA-2.3) — guía paso a paso

> **Contexto.** El repo ya tenía Alembic configurado (`alembic.ini`, `migrations/`)
> pero **nunca se ha ejecutado contra una base de datos real** — ni la local
> (`oraculo.db`, verificado: no tiene tabla `alembic_version`) ni, con toda
> probabilidad, la de producción en Supabase. El esquema se ha mantenido vivo
> hasta ahora con `ALTER TABLE` en caliente en cada arranque
> (`src/infrastructure/database_cloud.py::init_cloud_db`).
>
> Esta guía adopta Alembic de verdad, de forma segura, sin asumir en qué
> estado exacto está el esquema de tu base de datos de producción (que no
> puedo inspeccionar desde aquí). Ejecuta estos pasos **en tu máquina con
> Docker**, con calma, uno a uno.

## Qué se preparó ya (código, verificado localmente)

- **Nueva migración** [`migrations/versions/d4283e0fbed1_add_missing_user_showcase_columns.py`](../migrations/versions/d4283e0fbed1_add_missing_user_showcase_columns.py):
  añade las 4 columnas de `users` (`is_public_showcase`, `telegram_chat_id`,
  `pc_image_path`, `mobile_image_path`) que hasta ahora solo se creaban en
  caliente. **Es idempotente**: comprueba si cada columna ya existe antes de
  añadirla, así que es segura tanto si tu base de datos de producción ya las
  tiene (lo más probable) como si no. Probado en local con dos escenarios
  (columnas ya presentes / columnas ausentes) y con el downgrade — los tres
  casos funcionan correctamente.
- **`docker-entrypoint.sh`**: ejecuta `alembic upgrade head` antes de arrancar
  el servidor. Si la migración fallara por cualquier motivo, **no bloquea el
  arranque** — `init_cloud_db()` sigue funcionando como red de seguridad
  redundante (ya no traga errores en silencio, ver commit `aaa-2.4`) hasta que
  confirmes que la cadena de Alembic corre limpia contra tu base real.
- **`Dockerfile`**: cablea ese entrypoint sin tocar el `CMD`/`command` que ya
  usan tus `docker-compose*.yml`.

## Paso a paso en tu máquina con Docker

### 1. Backup ANTES de tocar nada

- **Local (SQLite):** `.\backup_db.ps1` (ya existe en el repo).
- **Producción (Supabase/Postgres):** haz un backup desde el propio panel de
  Supabase (Database → Backups) o con `pg_dump` si tienes acceso directo a la
  cadena de conexión. No sigas sin esto — es una migración de verdad sobre
  producción.

### 2. Trae esta rama (`refactor/aaa-uplift`) a tu máquina con Docker

```
git fetch origin
git checkout refactor/aaa-uplift
git pull
```

### 3. Comprueba el estado actual de tu base de datos de producción

Conéctate a Supabase (SQL Editor del panel, o `psql`) y ejecuta:

```sql
SELECT EXISTS (
  SELECT FROM information_schema.tables WHERE table_name = 'alembic_version'
);
```

- Si devuelve `false` (lo esperado, dado que nunca se ha usado Alembic): sigue
  con el paso 4.
- Si devuelve `true`: alguien ya usó Alembic contra esta base antes de esta
  guía — para y avísame antes de continuar, la situación es distinta a la que
  he podido probar.

### 4. "Baseline": dile a Alembic que la base ya está al día con el historial existente

Como tu base de producción ya tiene el esquema (creado por `create_all()` +
los ALTER en caliente a lo largo del tiempo), NO quieres que Alembic intente
recrear todo desde cero — solo quieres que sepa "ya estás aquí":

```bash
docker compose -f docker-compose.prod.yml run --rm backend alembic stamp f48b00d4a369
```

Esto no modifica ninguna tabla de datos, solo crea la tabla `alembic_version`
y anota en qué punto del historial está tu base.

### 5. Aplica la nueva migración (añade las 4 columnas si faltan)

```bash
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

Deberías ver `Running upgrade f48b00d4a369 -> d4283e0fbed1`. Si las columnas
ya existían (lo más probable), la migración las detecta y no hace nada —
no debería dar error.

### 6. Despliega normalmente

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

A partir de ahora, el entrypoint ejecuta `alembic upgrade head`
automáticamente en cada arranque del contenedor — cualquier migración nueva
que añadamos en el futuro se aplicará sola.

### 7. Verifica

- Revisa los logs del contenedor backend: deberías ver `✅ Migraciones
  aplicadas correctamente.` al arrancar.
- Entra a la app con tu email+contraseña y confirma que todo funciona
  (login, colección, configuración).
- Opcional: repite la consulta SQL del paso 3 — ahora debería devolver `true`,
  y `SELECT version_num FROM alembic_version;` debería mostrar `d4283e0fbed1`.

## Qué queda pendiente tras esto (no lo hagas todavía)

Una vez confirmes que el paso 6 funciona sin problemas durante unos días,
podemos (en una sesión futura, con calma):

- Quitar por completo el `ALTER TABLE` en caliente de `init_cloud_db()` —
  ahora mismo se deja como red de seguridad redundante a propósito.
- Migrar el resto de cambios de esquema "ocultos" en el código (si los hay)
  a migraciones Alembic reales, en vez de lógica ad-hoc en Python.

No hay prisa por dar ese paso — el sistema actual (Alembic + red de seguridad
redundante) es seguro tal cual queda con esta guía.
