"""Add economy configuration fields to gamification_config

Revision ID: 017
Revises: 016
Create Date: 2025-12-29

Changes:
- Add configurable favor economy fields to gamification_config table
- Reacciones: earn_reaction_base, earn_first_reaction_day, limit_reactions_per_day
- Misiones: earn_mission_daily, earn_mission_weekly, earn_level_evaluation
- Rachas: earn_streak_7_days, earn_streak_30_days
- Easter eggs: earn_easter_egg_min, earn_easter_egg_max
- Referidos: earn_referral_active
- All fields have defaults aligned with FAVOR_REWARDS in formatters.py
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add economy configuration fields to gamification_config table.

    These fields allow admins to configure the favor economy without changing code.
    Values are aligned with FAVOR_REWARDS in bot/gamification/utils/formatters.py.
    """

    # Reacciones a publicaciones
    op.add_column(
        'gamification_config',
        sa.Column('earn_reaction_base', sa.Float(), nullable=False, server_default='0.1')
    )
    op.add_column(
        'gamification_config',
        sa.Column('earn_first_reaction_day', sa.Float(), nullable=False, server_default='0.5')
    )
    op.add_column(
        'gamification_config',
        sa.Column('limit_reactions_per_day', sa.Integer(), nullable=False, server_default='10')
    )

    # Misiones
    op.add_column(
        'gamification_config',
        sa.Column('earn_mission_daily', sa.Float(), nullable=False, server_default='1.0')
    )
    op.add_column(
        'gamification_config',
        sa.Column('earn_mission_weekly', sa.Float(), nullable=False, server_default='3.0')
    )
    op.add_column(
        'gamification_config',
        sa.Column('earn_level_evaluation', sa.Float(), nullable=False, server_default='5.0')
    )

    # Rachas
    op.add_column(
        'gamification_config',
        sa.Column('earn_streak_7_days', sa.Float(), nullable=False, server_default='2.0')
    )
    op.add_column(
        'gamification_config',
        sa.Column('earn_streak_30_days', sa.Float(), nullable=False, server_default='10.0')
    )

    # Easter eggs
    op.add_column(
        'gamification_config',
        sa.Column('earn_easter_egg_min', sa.Float(), nullable=False, server_default='2.0')
    )
    op.add_column(
        'gamification_config',
        sa.Column('earn_easter_egg_max', sa.Float(), nullable=False, server_default='5.0')
    )

    # Referidos
    op.add_column(
        'gamification_config',
        sa.Column('earn_referral_active', sa.Float(), nullable=False, server_default='5.0')
    )


def downgrade() -> None:
    """
    Remove economy configuration fields from gamification_config table.

    WARNING: This will delete all custom economy configuration.
    System will fallback to FAVOR_REWARDS in formatters.py.
    """

    # Remove all economy fields in reverse order
    op.drop_column('gamification_config', 'earn_referral_active')
    op.drop_column('gamification_config', 'earn_easter_egg_max')
    op.drop_column('gamification_config', 'earn_easter_egg_min')
    op.drop_column('gamification_config', 'earn_streak_30_days')
    op.drop_column('gamification_config', 'earn_streak_7_days')
    op.drop_column('gamification_config', 'earn_level_evaluation')
    op.drop_column('gamification_config', 'earn_mission_weekly')
    op.drop_column('gamification_config', 'earn_mission_daily')
    op.drop_column('gamification_config', 'limit_reactions_per_day')
    op.drop_column('gamification_config', 'earn_first_reaction_day')
    op.drop_column('gamification_config', 'earn_reaction_base')
