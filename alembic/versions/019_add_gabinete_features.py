"""Add Gabinete features (F4.1)

Revision ID: 019
Revises: 018
Create Date: 2024-12-30

Adds:
- Gabinete fields to shop_item_categories table
- Gabinete fields to shop_items table
- user_discounts table for discount tracking
- gabinete_notifications table for user notifications
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '019_add_gabinete_features'
down_revision: Union[str, None] = '018_add_archetype_behavior_tracking'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Gabinete features to shop module."""

    # ========================================
    # 1. Add Gabinete fields to shop_item_categories
    # ========================================
    op.add_column('shop_item_categories', sa.Column(
        'gabinete_category',
        sa.String(50),
        nullable=True
    ))
    op.add_column('shop_item_categories', sa.Column(
        'lucien_description',
        sa.Text(),
        nullable=True
    ))
    op.add_column('shop_item_categories', sa.Column(
        'min_level_to_view',
        sa.Integer(),
        nullable=False,
        server_default='1'
    ))
    op.add_column('shop_item_categories', sa.Column(
        'min_level_to_buy',
        sa.Integer(),
        nullable=False,
        server_default='1'
    ))
    op.add_column('shop_item_categories', sa.Column(
        'is_gabinete',
        sa.Boolean(),
        nullable=False,
        server_default='0'
    ))

    # Index for gabinete categories
    op.create_index(
        'idx_shop_category_gabinete',
        'shop_item_categories',
        ['is_gabinete']
    )

    # ========================================
    # 2. Add Gabinete fields to shop_items
    # ========================================
    op.add_column('shop_items', sa.Column(
        'lucien_description',
        sa.Text(),
        nullable=True
    ))
    op.add_column('shop_items', sa.Column(
        'purchase_message',
        sa.Text(),
        nullable=True
    ))
    op.add_column('shop_items', sa.Column(
        'post_use_message',
        sa.Text(),
        nullable=True
    ))
    op.add_column('shop_items', sa.Column(
        'min_level_to_view',
        sa.Integer(),
        nullable=False,
        server_default='1'
    ))
    op.add_column('shop_items', sa.Column(
        'min_level_to_buy',
        sa.Integer(),
        nullable=False,
        server_default='1'
    ))
    op.add_column('shop_items', sa.Column(
        'visibility',
        sa.String(20),
        nullable=False,
        server_default='public'
    ))
    op.add_column('shop_items', sa.Column(
        'gabinete_item_type',
        sa.String(50),
        nullable=True
    ))
    op.add_column('shop_items', sa.Column(
        'duration_hours',
        sa.Integer(),
        nullable=True
    ))
    op.add_column('shop_items', sa.Column(
        'available_from',
        sa.DateTime(),
        nullable=True
    ))
    op.add_column('shop_items', sa.Column(
        'available_until',
        sa.DateTime(),
        nullable=True
    ))
    op.add_column('shop_items', sa.Column(
        'event_name',
        sa.String(100),
        nullable=True
    ))
    op.add_column('shop_items', sa.Column(
        'is_limited',
        sa.Boolean(),
        nullable=False,
        server_default='0'
    ))
    op.add_column('shop_items', sa.Column(
        'total_stock',
        sa.Integer(),
        nullable=True
    ))

    # Indexes for shop_items gabinete fields
    op.create_index(
        'idx_shop_item_visibility',
        'shop_items',
        ['visibility']
    )
    op.create_index(
        'idx_shop_item_level',
        'shop_items',
        ['min_level_to_buy']
    )

    # ========================================
    # 3. Create user_discounts table
    # ========================================
    op.create_table(
        'user_discounts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('discount_source', sa.String(20), nullable=False),
        sa.Column('source_item_id', sa.Integer(),
                  sa.ForeignKey('shop_items.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('discount_percent', sa.Float(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
    )

    # Indexes for user_discounts
    op.create_index('idx_user_discount_user', 'user_discounts', ['user_id'])
    op.create_index('idx_user_discount_source', 'user_discounts', ['discount_source'])
    op.create_index('idx_user_discount_active', 'user_discounts', ['user_id', 'is_active'])

    # ========================================
    # 4. Create gabinete_notifications table
    # ========================================
    op.create_table(
        'gabinete_notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('item_id', sa.Integer(),
                  sa.ForeignKey('shop_items.id', ondelete='CASCADE'),
                  nullable=True),
        sa.Column('notification_type', sa.String(30), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('is_sent', sa.Boolean(), nullable=False, server_default='0'),
    )

    # Indexes for gabinete_notifications
    op.create_index('idx_gabinete_notif_user', 'gabinete_notifications', ['user_id'])
    op.create_index('idx_gabinete_notif_type', 'gabinete_notifications', ['notification_type'])
    op.create_index('idx_gabinete_notif_unread', 'gabinete_notifications', ['user_id', 'read_at'])
    op.create_index('idx_gabinete_notif_sent', 'gabinete_notifications', ['is_sent'])


def downgrade() -> None:
    """Remove Gabinete features from shop module."""

    # Drop gabinete_notifications table and indexes
    op.drop_index('idx_gabinete_notif_sent', 'gabinete_notifications')
    op.drop_index('idx_gabinete_notif_unread', 'gabinete_notifications')
    op.drop_index('idx_gabinete_notif_type', 'gabinete_notifications')
    op.drop_index('idx_gabinete_notif_user', 'gabinete_notifications')
    op.drop_table('gabinete_notifications')

    # Drop user_discounts table and indexes
    op.drop_index('idx_user_discount_active', 'user_discounts')
    op.drop_index('idx_user_discount_source', 'user_discounts')
    op.drop_index('idx_user_discount_user', 'user_discounts')
    op.drop_table('user_discounts')

    # Drop shop_items gabinete indexes
    op.drop_index('idx_shop_item_level', 'shop_items')
    op.drop_index('idx_shop_item_visibility', 'shop_items')

    # Remove shop_items gabinete columns
    op.drop_column('shop_items', 'total_stock')
    op.drop_column('shop_items', 'is_limited')
    op.drop_column('shop_items', 'event_name')
    op.drop_column('shop_items', 'available_until')
    op.drop_column('shop_items', 'available_from')
    op.drop_column('shop_items', 'duration_hours')
    op.drop_column('shop_items', 'gabinete_item_type')
    op.drop_column('shop_items', 'visibility')
    op.drop_column('shop_items', 'min_level_to_buy')
    op.drop_column('shop_items', 'min_level_to_view')
    op.drop_column('shop_items', 'post_use_message')
    op.drop_column('shop_items', 'purchase_message')
    op.drop_column('shop_items', 'lucien_description')

    # Drop shop_item_categories gabinete index
    op.drop_index('idx_shop_category_gabinete', 'shop_item_categories')

    # Remove shop_item_categories gabinete columns
    op.drop_column('shop_item_categories', 'is_gabinete')
    op.drop_column('shop_item_categories', 'min_level_to_buy')
    op.drop_column('shop_item_categories', 'min_level_to_view')
    op.drop_column('shop_item_categories', 'lucien_description')
    op.drop_column('shop_item_categories', 'gabinete_category')
