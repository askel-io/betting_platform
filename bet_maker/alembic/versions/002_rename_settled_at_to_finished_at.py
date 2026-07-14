"""rename settled_at to finished_at

Revision ID: 002
Revises: 001
Create Date: 2026-07-14

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("bets")}

    if "settled_at" in columns and "finished_at" not in columns:
        op.alter_column("bets", "settled_at", new_column_name="finished_at")


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("bets")}

    if "finished_at" in columns and "settled_at" not in columns:
        op.alter_column("bets", "finished_at", new_column_name="settled_at")
