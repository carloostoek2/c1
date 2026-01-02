<%!
from alembic.util import rev_id
%>
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}

"""

# revision identifiers, used by Alembic.
revision = '${up_revision}'
down_revision = '${down_revision}'
branch_labels = None
depends_on = None


def upgrade() -> None:
    ${upgrade_ops}


def downgrade() -> None:
    ${downgrade_ops}