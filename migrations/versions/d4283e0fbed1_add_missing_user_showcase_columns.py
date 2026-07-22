"""add_missing_user_showcase_columns

Revision ID: d4283e0fbed1
Revises: f48b00d4a369
Create Date: 2026-07-21 12:50:27.666588

Fase AAA-2.3: estas 4 columnas de `users` llevaban tiempo creandose en
caliente en cada arranque (src/infrastructure/database_cloud.py::init_cloud_db),
nunca via Alembic. Como ninguna base de datos real (local ni, con toda
probabilidad, la de produccion en Supabase) ha sido nunca versionada con
Alembic, no podemos asumir si estas columnas ya existen alli o no. Por eso
esta migracion comprueba la existencia de cada columna antes de anadirla,
en vez de asumir un estado de partida concreto - es segura de ejecutar
tanto si el arranque en caliente ya las creo como si no.

Ver docs/ALEMBIC_ADOPTION.md para el procedimiento de adopcion (baseline +
despliegue) antes de aplicar esta migracion contra una base de datos real.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4283e0fbed1'
down_revision: Union[str, Sequence[str], None] = 'f48b00d4a369'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_NEW_COLUMNS = [
    sa.Column('is_public_showcase', sa.Boolean(), nullable=True, server_default=sa.text('false')),
    sa.Column('telegram_chat_id', sa.String(), nullable=True),
    sa.Column('pc_image_path', sa.String(), nullable=True),
    sa.Column('mobile_image_path', sa.String(), nullable=True),
]


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {c["name"] for c in inspector.get_columns("users")}

    with op.batch_alter_table('users', schema=None) as batch_op:
        for column in _NEW_COLUMNS:
            if column.name not in existing_columns:
                batch_op.add_column(column.copy())


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {c["name"] for c in inspector.get_columns("users")}

    with op.batch_alter_table('users', schema=None) as batch_op:
        for column in reversed(_NEW_COLUMNS):
            if column.name in existing_columns:
                batch_op.drop_column(column.name)
