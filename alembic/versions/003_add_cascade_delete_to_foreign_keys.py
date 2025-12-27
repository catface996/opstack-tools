"""Add CASCADE delete to foreign keys.

Revision ID: 003
Revises: 002
Create Date: 2025-12-27

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add CASCADE delete to tool_versions and tool_executions foreign keys."""
    # Drop existing foreign key constraints
    op.drop_constraint("tool_versions_tool_id_fkey", "tool_versions", type_="foreignkey")
    op.drop_constraint("tool_executions_tool_id_fkey", "tool_executions", type_="foreignkey")

    # Recreate with CASCADE delete
    op.create_foreign_key(
        "tool_versions_tool_id_fkey",
        "tool_versions",
        "tools",
        ["tool_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "tool_executions_tool_id_fkey",
        "tool_executions",
        "tools",
        ["tool_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Remove CASCADE delete from foreign keys."""
    # Drop CASCADE foreign key constraints
    op.drop_constraint("tool_versions_tool_id_fkey", "tool_versions", type_="foreignkey")
    op.drop_constraint("tool_executions_tool_id_fkey", "tool_executions", type_="foreignkey")

    # Recreate without CASCADE
    op.create_foreign_key(
        "tool_versions_tool_id_fkey",
        "tool_versions",
        "tools",
        ["tool_id"],
        ["id"],
    )
    op.create_foreign_key(
        "tool_executions_tool_id_fkey",
        "tool_executions",
        "tools",
        ["tool_id"],
        ["id"],
    )
