"""add_campaigns_table

Revision ID: 005_add_campaigns_table
Revises: 004_add_assets_table
Create Date: 2026-08-08 16:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '005_add_campaigns_table'
down_revision: Union[str, None] = '004_add_assets_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create campaigns table
    op.create_table(
        'campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False, server_default='META'),
        sa.Column('objective', sa.String(length=100), nullable=False, server_default='CONVERSIONS'),
        sa.Column('daily_budget', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('external_campaign_id', sa.String(length=255), nullable=True),
        sa.Column('campaign_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_campaigns_product_id'), 'campaigns', ['product_id'], unique=False)
    op.create_index(op.f('ix_campaigns_platform'), 'campaigns', ['platform'], unique=False)
    op.create_index(op.f('ix_campaigns_status'), 'campaigns', ['status'], unique=False)
    op.create_index(op.f('ix_campaigns_external_campaign_id'), 'campaigns', ['external_campaign_id'], unique=False)

    # 2. Create ad_sets table
    op.create_table(
        'ad_sets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('targeting', sa.JSON(), nullable=True),
        sa.Column('daily_budget', sa.Float(), nullable=False, server_default='50.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('external_adset_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_ad_sets_campaign_id'), 'ad_sets', ['campaign_id'], unique=False)

    # 3. Create ads table
    op.create_table(
        'ads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('ad_set_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ad_sets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('headline', sa.String(length=255), nullable=True),
        sa.Column('primary_text', sa.Text(), nullable=True),
        sa.Column('call_to_action', sa.String(length=50), nullable=True, server_default='SHOP_NOW'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('external_ad_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_ads_ad_set_id'), 'ads', ['ad_set_id'], unique=False)
    op.create_index(op.f('ix_ads_asset_id'), 'ads', ['asset_id'], unique=False)


def downgrade() -> None:
    op.drop_table('ads')
    op.drop_table('ad_sets')
    op.drop_table('campaigns')
