"""enable rls on staged_imports and authorized_devices

Revision ID: f48b00d4a369
Revises: e905ab7993c4
Create Date: 2026-02-25 20:47:55.454063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f48b00d4a369'
down_revision: Union[str, Sequence[str], None] = 'e905ab7993c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE staged_imports ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE authorized_devices ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE staged_imports DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE authorized_devices DISABLE ROW LEVEL SECURITY;")
