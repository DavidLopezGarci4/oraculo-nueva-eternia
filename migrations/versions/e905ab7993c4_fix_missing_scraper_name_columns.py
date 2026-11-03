"""fix missing scraper_name columns

Revision ID: e905ab7993c4
Revises: 66c2ec769424
Create Date: 2026-01-24 01:55:03.776327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e905ab7993c4'
down_revision: Union[str, Sequence[str], None] = '66c2ec769424'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema (idempotent for pre-existing un-stamped databases)."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'blackcluded_items' in existing_tables:
        with op.batch_alter_table('blackcluded_items', schema=None) as batch_op:
            batch_op.alter_column('source_type',
                   existing_type=sa.VARCHAR(length=50),
                   nullable=False,
                   existing_server_default=sa.text("'Retail'"))
            batch_op.alter_column('reason',
                   existing_type=sa.VARCHAR(),
                   nullable=True)
            batch_op.alter_column('validation_status',
                   existing_type=sa.VARCHAR(length=50),
                   nullable=False,
                   existing_server_default=sa.text("'VALIDATED'"))
            batch_op.alter_column('anomaly_flags',
                   existing_type=sa.TEXT(),
                   type_=sa.String(),
                   existing_nullable=True)
            batch_op.alter_column('is_blocked',
                   existing_type=sa.BOOLEAN(),
                   nullable=False,
                   existing_server_default=sa.text('(FALSE)'))

    if 'collection_items' in existing_tables:
        ci_indexes = {ix['name'] for ix in inspector.get_indexes('collection_items')}
        with op.batch_alter_table('collection_items', schema=None) as batch_op:
            if 'ix_collection_items_owner_id' not in ci_indexes:
                batch_op.create_index(batch_op.f('ix_collection_items_owner_id'), ['owner_id'], unique=False)
            if 'ix_collection_items_product_id' not in ci_indexes:
                batch_op.create_index(batch_op.f('ix_collection_items_product_id'), ['product_id'], unique=False)

    if 'offers' in existing_tables:
        offers_cols = {c['name'] for c in inspector.get_columns('offers')}
        offers_indexes = {ix['name'] for ix in inspector.get_indexes('offers')}
        with op.batch_alter_table('offers', schema=None) as batch_op:
            if 'sale_type' not in offers_cols:
                batch_op.add_column(sa.Column('sale_type', sa.String(), nullable=True))
            if 'expiry_at' not in offers_cols:
                batch_op.add_column(sa.Column('expiry_at', sa.DateTime(), nullable=True))
            if 'bids_count' not in offers_cols:
                batch_op.add_column(sa.Column('bids_count', sa.Integer(), nullable=True))
            if 'time_left_raw' not in offers_cols:
                batch_op.add_column(sa.Column('time_left_raw', sa.String(), nullable=True))
            batch_op.alter_column('source_type',
                   existing_type=sa.VARCHAR(length=20),
                   nullable=True,
                   existing_server_default=sa.text("'retail'"))
            batch_op.alter_column('validation_status',
                   existing_type=sa.VARCHAR(),
                   nullable=True,
                   existing_server_default=sa.text("'VALIDATED'"))
            batch_op.alter_column('is_blocked',
                   existing_type=sa.BOOLEAN(),
                   nullable=True,
                   existing_server_default=sa.text('(FALSE)'))
            batch_op.alter_column('opportunity_score',
                   existing_type=sa.INTEGER(),
                   nullable=True,
                   existing_server_default=sa.text('0'))
            if 'ix_offers_product_id' not in offers_indexes:
                batch_op.create_index(batch_op.f('ix_offers_product_id'), ['product_id'], unique=False)
            if 'ix_offers_shop_name' not in offers_indexes:
                batch_op.create_index(batch_op.f('ix_offers_shop_name'), ['shop_name'], unique=False)
            if 'ix_offers_url' not in offers_indexes:
                batch_op.create_index(batch_op.f('ix_offers_url'), ['url'], unique=False)
            if 'origin_category' in offers_cols:
                batch_op.drop_column('origin_category')

    if 'pending_matches' in existing_tables:
        pm_cols = {c['name'] for c in inspector.get_columns('pending_matches')}
        with op.batch_alter_table('pending_matches', schema=None) as batch_op:
            if 'sale_type' not in pm_cols:
                batch_op.add_column(sa.Column('sale_type', sa.String(), nullable=True))
            if 'expiry_at' not in pm_cols:
                batch_op.add_column(sa.Column('expiry_at', sa.DateTime(), nullable=True))
            if 'bids_count' not in pm_cols:
                batch_op.add_column(sa.Column('bids_count', sa.Integer(), nullable=True))
            if 'time_left_raw' not in pm_cols:
                batch_op.add_column(sa.Column('time_left_raw', sa.String(), nullable=True))
            batch_op.alter_column('source_type',
                   existing_type=sa.VARCHAR(length=20),
                   nullable=True,
                   existing_server_default=sa.text("'retail'"))
            batch_op.alter_column('validation_status',
                   existing_type=sa.VARCHAR(),
                   nullable=True,
                   existing_server_default=sa.text("'PENDING'"))
            batch_op.alter_column('is_blocked',
                   existing_type=sa.BOOLEAN(),
                   nullable=True,
                   existing_server_default=sa.text('(FALSE)'))
            batch_op.alter_column('opportunity_score',
                   existing_type=sa.INTEGER(),
                   nullable=True,
                   existing_server_default=sa.text('0'))
            if 'origin_category' in pm_cols:
                batch_op.drop_column('origin_category')

    if 'price_history' in existing_tables:
        ph_cols = {c['name'] for c in inspector.get_columns('price_history')}
        if 'is_snapshot' not in ph_cols:
            with op.batch_alter_table('price_history', schema=None) as batch_op:
                batch_op.add_column(sa.Column('is_snapshot', sa.Boolean(), nullable=True))

    if 'scraper_execution_logs' in existing_tables:
        exec_cols = {c['name'] for c in inspector.get_columns('scraper_execution_logs')}
        exec_indexes = {ix['name'] for ix in inspector.get_indexes('scraper_execution_logs')}
        if 'spider_name' not in exec_cols:
            with op.batch_alter_table('scraper_execution_logs', schema=None) as batch_op:
                batch_op.add_column(sa.Column('spider_name', sa.String(), nullable=True))
                if 'ix_scraper_execution_logs_spider_name' not in exec_indexes:
                    batch_op.create_index(batch_op.f('ix_scraper_execution_logs_spider_name'), ['spider_name'], unique=False)

    if 'scraper_status' in existing_tables:
        status_cols = {c['name'] for c in inspector.get_columns('scraper_status')}
        if 'spider_name' not in status_cols:
            with op.batch_alter_table('scraper_status', schema=None) as batch_op:
                batch_op.add_column(sa.Column('spider_name', sa.String(), nullable=True))

    if 'users' in existing_tables:
        users_cols = {c['name'] for c in inspector.get_columns('users')}
        if 'location' not in users_cols:
            with op.batch_alter_table('users', schema=None) as batch_op:
                batch_op.add_column(sa.Column('location', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'location')
    op.drop_column('price_history', 'is_snapshot')
    op.add_column('pending_matches', sa.Column('origin_category', sa.VARCHAR(length=20), server_default=sa.text("'retail'"), nullable=True))
    op.alter_column('pending_matches', 'opportunity_score',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))
    op.alter_column('pending_matches', 'is_blocked',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('(FALSE)'))
    op.alter_column('pending_matches', 'validation_status',
               existing_type=sa.VARCHAR(),
               nullable=True,
               existing_server_default=sa.text("'PENDING'"))
    op.alter_column('pending_matches', 'source_type',
               existing_type=sa.VARCHAR(length=20),
               nullable=True,
               existing_server_default=sa.text("'retail'"))
    op.drop_column('pending_matches', 'time_left_raw')
    op.drop_column('pending_matches', 'bids_count')
    op.drop_column('pending_matches', 'expiry_at')
    op.drop_column('pending_matches', 'sale_type')
    op.add_column('offers', sa.Column('origin_category', sa.VARCHAR(length=20), server_default=sa.text("'retail'"), nullable=True))
    op.drop_index(op.f('ix_offers_url'), table_name='offers')
    op.drop_index(op.f('ix_offers_shop_name'), table_name='offers')
    op.drop_index(op.f('ix_offers_product_id'), table_name='offers')
    op.alter_column('offers', 'opportunity_score',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))
    op.alter_column('offers', 'is_blocked',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('(FALSE)'))
    op.alter_column('offers', 'validation_status',
               existing_type=sa.VARCHAR(),
               nullable=True,
               existing_server_default=sa.text("'VALIDATED'"))
    op.alter_column('offers', 'source_type',
               existing_type=sa.VARCHAR(length=20),
               nullable=True,
               existing_server_default=sa.text("'retail'"))
    op.drop_column('offers', 'time_left_raw')
    op.drop_column('offers', 'bids_count')
    op.drop_column('offers', 'expiry_at')
    op.drop_column('offers', 'sale_type')
    op.add_column('kaizen_insights', sa.Column('spider_name', sa.VARCHAR(), nullable=False))
    op.drop_index(op.f('ix_kaizen_insights_scraper_name'), table_name='kaizen_insights')
    op.create_index(op.f('ix_kaizen_insights_spider_name'), 'kaizen_insights', ['spider_name'], unique=False)
    op.drop_column('kaizen_insights', 'scraper_name')
    op.drop_index(op.f('ix_collection_items_product_id'), table_name='collection_items')
    op.drop_index(op.f('ix_collection_items_owner_id'), table_name='collection_items')
    op.alter_column('blackcluded_items', 'is_blocked',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('(FALSE)'))
    op.alter_column('blackcluded_items', 'anomaly_flags',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('blackcluded_items', 'validation_status',
               existing_type=sa.VARCHAR(length=50),
               nullable=True,
               existing_server_default=sa.text("'VALIDATED'"))
    op.alter_column('blackcluded_items', 'reason',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('blackcluded_items', 'source_type',
               existing_type=sa.VARCHAR(length=50),
               nullable=True,
               existing_server_default=sa.text("'Retail'"))
    # ### end Alembic commands ###
