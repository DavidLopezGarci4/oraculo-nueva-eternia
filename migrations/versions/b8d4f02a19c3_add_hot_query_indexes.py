"""add_hot_query_indexes

Revision ID: b8d4f02a19c3
Revises: a7c3e91f04b2
Create Date: 2026-11-13 21:20:00.000000

Añade de forma idempotente los índices compuestos sobre `offers` y `pending_matches`
para acelerar consultas del Dashboard, Purgatorio y sincronización de disponibilidad.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b8d4f02a19c3"
down_revision: Union[str, Sequence[str], None] = "a7c3e91f04b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_HOT_INDEXES = (
    ("offers", "ix_offers_avail_source_last_seen", ["is_available", "source_type", "last_seen"]),
    ("offers", "ix_offers_shop_avail_vintage", ["shop_name", "is_available", "is_vintage"]),
    ("pending_matches", "ix_pending_matches_status_found_at", ["validation_status", "found_at"]),
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table_name, index_name, columns in _HOT_INDEXES:
        if table_name not in existing_tables:
            continue
        existing_idx = {idx["name"] for idx in inspector.get_indexes(table_name)}
        if index_name not in existing_idx:
            op.create_index(index_name, table_name, columns, unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table_name, index_name, _columns in reversed(_HOT_INDEXES):
        if table_name not in existing_tables:
            continue
        existing_idx = {idx["name"] for idx in inspector.get_indexes(table_name)}
        if index_name in existing_idx:
            op.drop_index(index_name, table_name=table_name)
