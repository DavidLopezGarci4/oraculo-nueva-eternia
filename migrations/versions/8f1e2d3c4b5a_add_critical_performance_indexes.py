"""add_critical_performance_indexes

Revision ID: 8f1e2d3c4b5a
Revises: feac3ac24f77
Create Date: 2026-09-22 22:00:00.000000

Optimización de rendimiento (Bloque 2):
Añade índices clave para eliminar table scans en consultas de catálogo,
colección, alertas del centinela, scrapers y cola de sincronización.
Es completamente idempotente (comprueba índices existentes antes de crearlos).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f1e2d3c4b5a'
down_revision: Union[str, Sequence[str], None] = 'feac3ac24f77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (table, index_name, [columns])
_NEW_INDEXES = [
    ("offers", "ix_offers_product_id_is_available", ["product_id", "is_available"]),
    ("offers", "ix_offers_price", ["price"]),
    ("collection_items", "ix_collection_items_owner_id_acquired", ["owner_id", "acquired"]),
    ("price_alerts", "ix_price_alerts_user_product_active", ["user_id", "product_id", "is_active"]),
    ("scraper_status", "ix_scraper_status_spider_name", ["spider_name"]),
    ("sync_queue", "ix_sync_queue_status", ["status"]),
]


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table, index_name, columns in _NEW_INDEXES:
        if table in existing_tables:
            existing_indexes = {ix["name"] for ix in inspector.get_indexes(table)}
            if index_name not in existing_indexes:
                op.create_index(index_name, table, columns)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table, index_name, _columns in reversed(_NEW_INDEXES):
        if table in existing_tables:
            existing_indexes = {ix["name"] for ix in inspector.get_indexes(table)}
            if index_name in existing_indexes:
                op.drop_index(index_name, table_name=table)
