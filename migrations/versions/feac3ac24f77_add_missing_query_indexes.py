"""add_missing_query_indexes

Revision ID: feac3ac24f77
Revises: d4283e0fbed1
Create Date: 2026-07-21 17:52:13.074960

Fase AAA-3e: auditoria de `EXPLAIN QUERY PLAN` contra las consultas reales
de catalogo/coleccion/purgatorio (ver docs/REPORTE_MEJORAS_AAA.md, item 3e)
encontro varias columnas filtradas/ordenadas con frecuencia sin indice,
forzando un SCAN de tabla completa o un TEMP B-TREE para el ORDER BY. Esta
migracion las anade. Idempotente (comprueba los indices existentes antes de
crear cada uno) por la misma razon que d4283e0fbed1: ninguna base de datos
real ha sido nunca versionada con Alembic, asi que no podemos asumir un
estado de partida concreto.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'feac3ac24f77'
down_revision: Union[str, Sequence[str], None] = 'd4283e0fbed1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (table, index_name, [columns])
_NEW_INDEXES = [
    ("products", "ix_products_category", ["category"]),
    ("offers", "ix_offers_last_seen", ["last_seen"]),
    ("offers", "ix_offers_opportunity_score", ["opportunity_score"]),
    ("collection_items", "ix_collection_items_acquired", ["acquired"]),
    ("pending_matches", "ix_pending_matches_validation_status", ["validation_status"]),
    ("pending_matches", "ix_pending_matches_found_at", ["found_at"]),
    ("offer_history", "ix_offer_history_timestamp", ["timestamp"]),
    ("price_history", "ix_price_history_offer_id", ["offer_id"]),
    ("price_history", "ix_price_history_recorded_at", ["recorded_at"]),
]


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for table, index_name, columns in _NEW_INDEXES:
        existing = {ix["name"] for ix in inspector.get_indexes(table)}
        if index_name not in existing:
            op.create_index(index_name, table, columns)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for table, index_name, _columns in reversed(_NEW_INDEXES):
        existing = {ix["name"] for ix in inspector.get_indexes(table)}
        if index_name in existing:
            op.drop_index(index_name, table_name=table)
