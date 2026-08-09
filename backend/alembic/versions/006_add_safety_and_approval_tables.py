"""add_safety_and_approval_tables

Revision ID: 006_add_safety_and_approval_tables
Revises: 005_add_campaigns_table
Create Date: 2026-08-08 16:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '006_add_safety_and_approval_tables'
down_revision: Union[str, None] = '005_add_campaigns_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create policy_rules table
    op.create_table(
        'policy_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('rule_type', sa.String(length=100), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_policy_rules_rule_type'), 'policy_rules', ['rule_type'], unique=False)
    op.create_index(op.f('ix_policy_rules_is_active'), 'policy_rules', ['is_active'], unique=False)

    # 2. Create approval_requests table
    op.create_table(
        'approval_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('requested_action', sa.String(length=100), nullable=False),
        sa.Column('requested_by', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('reviewed_by', sa.String(length=255), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_approval_requests_campaign_id'), 'approval_requests', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_approval_requests_requested_action'), 'approval_requests', ['requested_action'], unique=False)
    op.create_index(op.f('ix_approval_requests_status'), 'approval_requests', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('approval_requests')
    op.drop_table('policy_rules')
