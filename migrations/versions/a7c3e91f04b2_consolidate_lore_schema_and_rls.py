"""consolidate_lore_schema_and_rls

Revision ID: a7c3e91f04b2
Revises: 9b4c7d8e1f2a
Create Date: 2026-11-09 10:10:00.000000

Sustituye los `ALTER TABLE character_lore` que se ejecutaban en cada arranque de FastAPI
(`init_cloud_db`) por una migracion idempotente:
1. Crea `character_lore` / `product_lore` si no existen (segun los modelos ORM).
2. Anade de forma idempotente las columnas historicas de `character_lore`.
3. En PostgreSQL habilita RLS y revoca privilegios a `anon` / `authenticated`.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a7c3e91f04b2"
down_revision: Union[str, Sequence[str], None] = "9b4c7d8e1f2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_LEGACY_CHARACTER_LORE_COLUMNS = (
    ("subtitle", sa.String(), None),
    ("flavor_quote_author", sa.String(), None),
    ("text_color", sa.String(), "'#FFFFFF'"),
    ("card_version", sa.String(), "'showcase'"),
    ("mana_cost", sa.String(), "'{2}{W}{W}'"),
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    from src.domain.models import Base

    for table_name in ("character_lore", "product_lore"):
        if table_name not in existing_tables:
            Base.metadata.tables[table_name].create(bind=bind, checkfirst=True)

    inspector = sa.inspect(bind)
    current_cols = {c["name"] for c in inspector.get_columns("character_lore")}
    for name, col_type, server_default in _LEGACY_CHARACTER_LORE_COLUMNS:
        if name not in current_cols:
            op.add_column(
                "character_lore",
                sa.Column(
                    name,
                    col_type,
                    nullable=True,
                    server_default=sa.text(server_default) if server_default else None,
                ),
            )

    if bind.dialect.name == "postgresql":
        for table_name in ("character_lore", "product_lore"):
            op.execute(f"ALTER TABLE public.{table_name} ENABLE ROW LEVEL SECURITY;")
            op.execute(f"REVOKE ALL ON TABLE public.{table_name} FROM anon, authenticated;")


def downgrade() -> None:
    # Invariante Zero-Trust: nunca se desactiva RLS ni se reabren privilegios publicos.
    pass
