"""Add script_content column to tool_versions table.

Revision ID: 002
Revises: 001
Create Date: 2025-12-26

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add script_content column to tool_versions table."""
    op.add_column("tool_versions", sa.Column("script_content", sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove script_content column from tool_versions table."""
    op.drop_column("tool_versions", "script_content")
