"""add_campaign_metrics_table

Revision ID: 007_add_campaign_metrics_table
Revises: 006_add_safety_and_approval_tables
Create Date: 2026-08-08 16:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '007_add_campaign_metrics_table'
down_revision: Union[str, None] = '006_add_safety_and_approval_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create campaign_metrics table
    op.create_table(
        'campaign_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ad_set_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ad_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=False, server_default='META'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('impressions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('clicks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('spend_usd', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('conversions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ctr', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('cpa_usd', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('roas', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_campaign_metrics_campaign_id'), 'campaign_metrics', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_campaign_metrics_platform'), 'campaign_metrics', ['platform'], unique=False)
    op.create_index(op.f('ix_campaign_metrics_recorded_at'), 'campaign_metrics', ['recorded_at'], unique=False)


def downgrade() -> None:
    op.drop_table('campaign_metrics')
