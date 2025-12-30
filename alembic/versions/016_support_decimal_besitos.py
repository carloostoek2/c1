"""Support decimal besitos for favor economy

Revision ID: 016
Revises: 015
Create Date: 2025-12-29

Changes:
- Convert besitos fields from Integer to Float to support decimal values (0.1, 0.5, etc.)
- Affects user_gamification: total_besitos, besitos_earned, besitos_spent
- Affects besito_transactions: amount, balance_after
- Preserves existing data by converting integers to floats
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Convert besitos-related fields from Integer to Float.

    This enables the favor economy to use decimal values like:
    - 0.1 Favores for basic reaction
    - 0.5 Favores for first daily reaction
    - 1.0 Favores for daily mission

    SQLite will handle the type change automatically, converting existing
    integer values to floats (10 → 10.0).
    """

    # ============================================================
    # TABLE: user_gamification
    # ============================================================

    # Note: SQLite doesn't support ALTER COLUMN directly.
    # We need to recreate the table with new types.

    # Step 1: Create new table with Float columns
    op.execute("""
        CREATE TABLE user_gamification_new (
            user_id INTEGER NOT NULL PRIMARY KEY,
            total_besitos REAL NOT NULL DEFAULT 0,
            besitos_earned REAL NOT NULL DEFAULT 0,
            besitos_spent REAL NOT NULL DEFAULT 0,
            current_level_id INTEGER,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users (user_id) ON DELETE CASCADE,
            FOREIGN KEY(current_level_id) REFERENCES levels (id)
        )
    """)

    # Step 2: Copy data from old table (integers will be converted to floats)
    op.execute("""
        INSERT INTO user_gamification_new (
            user_id, total_besitos, besitos_earned, besitos_spent,
            current_level_id, created_at, updated_at
        )
        SELECT
            user_id,
            CAST(total_besitos AS REAL),
            CAST(besitos_earned AS REAL),
            CAST(besitos_spent AS REAL),
            current_level_id,
            created_at,
            updated_at
        FROM user_gamification
    """)

    # Step 3: Drop old table
    op.execute("DROP TABLE user_gamification")

    # Step 4: Rename new table
    op.execute("ALTER TABLE user_gamification_new RENAME TO user_gamification")

    # Step 5: Recreate index
    op.create_index(
        'ix_user_gamification_total_besitos',
        'user_gamification',
        ['total_besitos'],
        unique=False
    )

    # ============================================================
    # TABLE: besito_transactions
    # ============================================================

    # Step 1: Create new table with Float columns
    op.execute("""
        CREATE TABLE besito_transactions_new (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            description VARCHAR(500) NOT NULL,
            reference_id INTEGER,
            balance_after REAL NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )
    """)

    # Step 2: Copy data
    op.execute("""
        INSERT INTO besito_transactions_new (
            id, user_id, amount, transaction_type, description,
            reference_id, balance_after, created_at
        )
        SELECT
            id, user_id,
            CAST(amount AS REAL),
            transaction_type, description,
            reference_id,
            CAST(balance_after AS REAL),
            created_at
        FROM besito_transactions
    """)

    # Step 3: Drop old table
    op.execute("DROP TABLE besito_transactions")

    # Step 4: Rename new table
    op.execute("ALTER TABLE besito_transactions_new RENAME TO besito_transactions")

    # Step 5: Recreate indexes
    op.create_index(
        'idx_user_transactions_history',
        'besito_transactions',
        ['user_id', 'created_at'],
        unique=False
    )

    op.create_index(
        'idx_user_transaction_type',
        'besito_transactions',
        ['user_id', 'transaction_type'],
        unique=False
    )

    op.create_index(
        'idx_reference_transaction',
        'besito_transactions',
        ['reference_id', 'transaction_type'],
        unique=False
    )


def downgrade() -> None:
    """
    Revert Float columns back to Integer.

    WARNING: This will truncate decimal values!
    0.1 → 0, 1.5 → 1, etc.
    """

    # ============================================================
    # TABLE: user_gamification
    # ============================================================

    # Drop index first
    op.drop_index('ix_user_gamification_total_besitos', table_name='user_gamification')

    # Create old table structure
    op.execute("""
        CREATE TABLE user_gamification_old (
            user_id INTEGER NOT NULL PRIMARY KEY,
            total_besitos INTEGER NOT NULL DEFAULT 0,
            besitos_earned INTEGER NOT NULL DEFAULT 0,
            besitos_spent INTEGER NOT NULL DEFAULT 0,
            current_level_id INTEGER,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users (user_id) ON DELETE CASCADE,
            FOREIGN KEY(current_level_id) REFERENCES levels (id)
        )
    """)

    # Copy data (truncate decimals)
    op.execute("""
        INSERT INTO user_gamification_old (
            user_id, total_besitos, besitos_earned, besitos_spent,
            current_level_id, created_at, updated_at
        )
        SELECT
            user_id,
            CAST(total_besitos AS INTEGER),
            CAST(besitos_earned AS INTEGER),
            CAST(besitos_spent AS INTEGER),
            current_level_id,
            created_at,
            updated_at
        FROM user_gamification
    """)

    # Drop new table
    op.execute("DROP TABLE user_gamification")

    # Rename
    op.execute("ALTER TABLE user_gamification_old RENAME TO user_gamification")

    # Recreate index
    op.create_index(
        'ix_user_gamification_total_besitos',
        'user_gamification',
        ['total_besitos'],
        unique=False
    )

    # ============================================================
    # TABLE: besito_transactions
    # ============================================================

    # Drop indexes
    op.drop_index('idx_reference_transaction', table_name='besito_transactions')
    op.drop_index('idx_user_transaction_type', table_name='besito_transactions')
    op.drop_index('idx_user_transactions_history', table_name='besito_transactions')

    # Create old table
    op.execute("""
        CREATE TABLE besito_transactions_old (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            description VARCHAR(500) NOT NULL,
            reference_id INTEGER,
            balance_after INTEGER NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )
    """)

    # Copy data (truncate decimals)
    op.execute("""
        INSERT INTO besito_transactions_old (
            id, user_id, amount, transaction_type, description,
            reference_id, balance_after, created_at
        )
        SELECT
            id, user_id,
            CAST(amount AS INTEGER),
            transaction_type, description,
            reference_id,
            CAST(balance_after AS INTEGER),
            created_at
        FROM besito_transactions
    """)

    # Drop new table
    op.execute("DROP TABLE besito_transactions")

    # Rename
    op.execute("ALTER TABLE besito_transactions_old RENAME TO besito_transactions")

    # Recreate indexes
    op.create_index(
        'idx_user_transactions_history',
        'besito_transactions',
        ['user_id', 'created_at'],
        unique=False
    )

    op.create_index(
        'idx_user_transaction_type',
        'besito_transactions',
        ['user_id', 'transaction_type'],
        unique=False
    )

    op.create_index(
        'idx_reference_transaction',
        'besito_transactions',
        ['reference_id', 'transaction_type'],
        unique=False
    )
