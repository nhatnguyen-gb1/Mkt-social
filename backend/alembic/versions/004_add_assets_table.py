"""add_assets_table

Revision ID: 004_add_assets_table
Revises: 003_add_agent_runs_and_llm_usage
Create Date: 2026-08-08 16:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '004_add_assets_table'
down_revision: Union[str, None] = '003_add_agent_runs_and_llm_usage'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('agent_run_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('asset_type', sa.String(length=50), nullable=False, server_default='IMAGE'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('file_url', sa.String(length=2048), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=True),
        sa.Column('asset_metadata', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_assets_product_id'), 'assets', ['product_id'], unique=False)
    op.create_index(op.f('ix_assets_agent_run_id'), 'assets', ['agent_run_id'], unique=False)
    op.create_index(op.f('ix_assets_asset_type'), 'assets', ['asset_type'], unique=False)
    op.create_index(op.f('ix_assets_status'), 'assets', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('assets')
