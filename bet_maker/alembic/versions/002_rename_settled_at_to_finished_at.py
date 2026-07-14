"""rename settled_at to finished_at

Revision ID: 002
Revises: 001
Create Date: 2026-07-14

"""

from collections.abc import Sequence

from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("bets", "settled_at", new_column_name="finished_at")


def downgrade() -> None:
    op.alter_column("bets", "finished_at", new_column_name="settled_at")
