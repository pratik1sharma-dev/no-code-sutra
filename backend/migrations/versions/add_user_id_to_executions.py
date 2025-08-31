"""Add user_id to executions table

Revision ID: add_user_id_to_executions
Revises: create_workflow_permissions
Create Date: 2025-08-31 23:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'add_user_id_to_executions'
down_revision = 'create_workflow_permissions'
branch_labels = None
depends_on = None


def upgrade():
    # Add user_id column to executions table
    op.add_column('executions', sa.Column('user_id', sa.String(), nullable=True))
    
    # Add indexes for better query performance
    op.create_index(op.f('ix_executions_user_id'), 'executions', ['user_id'], unique=False)
    op.create_index(op.f('ix_executions_workflow_id'), 'executions', ['workflow_id'], unique=False)
    op.create_index(op.f('ix_executions_status'), 'executions', ['status'], unique=False)
    op.create_index(op.f('ix_executions_started_at'), 'executions', ['started_at'], unique=False)
    
    # Create composite indexes for common query patterns
    op.create_index('idx_execution_workflow_user', 'executions', ['workflow_id', 'user_id'], unique=False)
    op.create_index('idx_execution_status_time', 'executions', ['status', 'started_at'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index('idx_execution_status_time', table_name='executions')
    op.drop_index('idx_execution_workflow_user', table_name='executions')
    op.drop_index(op.f('ix_executions_started_at'), table_name='executions')
    op.drop_index(op.f('ix_executions_status'), table_name='executions')
    op.drop_index(op.f('ix_executions_workflow_id'), table_name='executions')
    op.drop_index(op.f('ix_executions_user_id'), table_name='executions')
    
    # Drop user_id column
    op.drop_column('executions', 'user_id')
