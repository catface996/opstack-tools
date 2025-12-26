"""Add script_content column to tools table.

Revision ID: 001
Revises:
Create Date: 2025-12-26

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add script_content column to tools table."""
    op.add_column("tools", sa.Column("script_content", sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove script_content column from tools table."""
    op.drop_column("tools", "script_content")
