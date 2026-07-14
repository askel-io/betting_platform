"""rename settled_at to finished_at

Revision ID: 002
Revises: 001
Create Date: 2026-07-14

"""
from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("bets", "settled_at", new_column_name="finished_at")


def downgrade() -> None:
    op.alter_column("bets", "finished_at", new_column_name="settled_at")
