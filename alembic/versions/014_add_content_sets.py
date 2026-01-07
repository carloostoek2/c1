"""
Migración: Crear tablas para CMS Journey - Content Sets

Agrega tablas para gestión de contenido multimedia que se integra
con shop, narrativa y gamificación.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = 'add_content_sets'
down_revision = None  # Ajustar según tu versión anterior
branch_labels = None
depends_on = None


def upgrade():
    """Crear tablas de content sets y extender tablas existentes."""

    # ============================================================
    # TABLA: content_sets
    # ============================================================
    op.create_table(
        'content_sets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_type', sa.String(20), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('tier', sa.String(20), nullable=False),
        sa.Column('file_ids_json', sa.Text(), nullable=True),
        sa.Column('file_metadata_json', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('requires_vip', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id']),
        sa.Index('idx_content_slug', 'slug'),
        sa.Index('idx_content_type_tier', 'content_type', 'tier'),
        sa.Index('idx_content_active', 'is_active')
    )

    # ============================================================
    # TABLA: user_content_access
    # ============================================================
    op.create_table(
        'user_content_access',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('content_set_id', sa.Integer(), nullable=False),
        sa.Column('accessed_at', sa.DateTime(), nullable=False),
        sa.Column('delivery_context', sa.String(100), nullable=True),
        sa.Column('trigger_type', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['content_set_id'], ['content_sets.id']),
        sa.Index('idx_user_content', 'user_id', 'content_set_id'),
        sa.Index('idx_content_access_by_user', 'user_id', 'accessed_at')
    )

    # ============================================================
    # EXTENSIÓN: shop_items
    # ============================================================
    with op.batch_alter_table('shop_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content_set_id', sa.Integer(), nullable=True))

    # Crear índice para content_set_id
    op.create_index(
        'idx_shop_item_content_set',
        'shop_items',
        ['content_set_id']
    )

    # Crear foreign key
    op.create_foreign_key(
        'fk_shop_item_content_set',
        'shop_items',
        'content_sets',
        ['content_set_id'],
        ['id']
    )

    # ============================================================
    # EXTENSIÓN: narrative_fragments
    # ============================================================
    with op.batch_alter_table('narrative_fragments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content_set_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('auto_send_content', sa.Boolean(), nullable=False))

    # Crear índice para content_set_id
    op.create_index(
        'idx_fragment_content_set',
        'narrative_fragments',
        ['content_set_id']
    )

    # Crear foreign keys
    op.create_foreign_key(
        'fk_fragment_content_set',
        'narrative_fragments',
        'content_sets',
        ['content_set_id'],
        ['id']
    )

    # ============================================================
    # EXTENSIÓN: rewards
    # ============================================================
    with op.batch_alter_table('rewards', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content_set_id', sa.Integer(), nullable=True))

    # Crear índice para content_set_id
    op.create_index(
        'idx_reward_content_set',
        'rewards',
        ['content_set_id']
    )

    # Crear foreign key
    op.create_foreign_key(
        'fk_reward_content_set',
        'rewards',
        'content_sets',
        ['content_set_id'],
        ['id']
    )


def downgrade():
    """Revertir todos los cambios."""

    # Eliminar índices y foreign keys en orden inverso

    # Rewards
    op.drop_constraint('fk_reward_content_set', 'rewards')
    op.drop_index('idx_reward_content_set', 'rewards')
    with op.batch_alter_table('rewards', schema=None) as batch_op:
        batch_op.drop_column('content_set_id')

    # Narrative Fragments
    op.drop_constraint('fk_fragment_content_set', 'narrative_fragments')
    op.drop_index('idx_fragment_content_set', 'narrative_fragments')
    with op.batch_alter_table('narrative_fragments', schema=None) as batch_op:
        batch_op.drop_column('auto_send_content')
        batch_op.drop_column('content_set_id')

    # Shop Items
    op.drop_constraint('fk_shop_item_content_set', 'shop_items')
    op.drop_index('idx_shop_item_content_set', 'shop_items')
    with op.batch_alter_table('shop_items', schema=None) as batch_op:
        batch_op.drop_column('content_set_id')

    # User Content Access
    op.drop_table('user_content_access')

    # Content Sets
    op.drop_table('content_sets')
