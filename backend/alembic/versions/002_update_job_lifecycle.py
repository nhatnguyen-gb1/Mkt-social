"""update_job_lifecycle

Revision ID: 002_update_job_lifecycle
Revises: 001_initial_schema
Create Date: 2026-08-07 15:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_update_job_lifecycle'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('jobs', sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('jobs', sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'))
    op.add_column('jobs', sa.Column('started_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('jobs', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('jobs', sa.Column('created_by_telegram_id', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_jobs_created_by_telegram_id'), 'jobs', ['created_by_telegram_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_jobs_created_by_telegram_id'), table_name='jobs')
    op.drop_column('jobs', 'created_by_telegram_id')
    op.drop_column('jobs', 'completed_at')
    op.drop_column('jobs', 'started_at')
    op.drop_column('jobs', 'max_retries')
    op.drop_column('jobs', 'retry_count')
