#!/bin/sh
# Fase AAA-2.3: aplica las migraciones de Alembic antes de arrancar la API.
#
# No bloqueamos el arranque si la migracion falla: init_cloud_db() (ver
# src/infrastructure/database_cloud.py) sigue actuando como red de seguridad
# redundante e idempotente para el esquema de `users` mientras se confirma,
# en un despliegue real, que la cadena de migraciones aplica limpiamente
# contra la base de datos de produccion (ver docs/ALEMBIC_ADOPTION.md antes
# del primer despliegue con este cambio).
set -u

# Solo ejecutar upgrade automatico si el comando es arrancar el servidor uvicorn
if [ "$#" -gt 0 ] && [ "$1" = "uvicorn" ]; then
    echo "🗃️  Aplicando migraciones de Alembic..."
    if alembic upgrade head; then
        echo "✅ Migraciones aplicadas correctamente."
    else
        echo "⚠️  Alembic fallo o no pudo aplicar migraciones. Continuando arranque:" \
             "init_cloud_db() cubre el esquema minimo necesario como red de seguridad." >&2
    fi
fi

exec "$@"
