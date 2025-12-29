"""
Add user activity tracking fields.

Adds last_activity and is_new_user fields to users table
for tracking user engagement and onboarding status.

Revision ID: 015
Revises: 014
Create Date: 2024-12-29
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add activity tracking columns to users table."""
    # Add last_activity column (nullable)
    op.add_column(
        'users',
        sa.Column('last_activity', sa.DateTime(), nullable=True)
    )

    # Add is_new_user column with default True
    op.add_column(
        'users',
        sa.Column('is_new_user', sa.Boolean(), nullable=False, server_default='1')
    )

    # For existing users, set is_new_user to False (they already went through some flow)
    op.execute("UPDATE users SET is_new_user = 0 WHERE is_new_user = 1")


def downgrade() -> None:
    """Remove activity tracking columns."""
    op.drop_column('users', 'is_new_user')
    op.drop_column('users', 'last_activity')
