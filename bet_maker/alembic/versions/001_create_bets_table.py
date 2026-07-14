"""create bets table

Revision ID: 001
Revises:
Create Date: 2026-07-14

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bets",
        sa.Column("bet_id", sa.String(), nullable=False),
        sa.Column("event_id", sa.String(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("bet_id"),
    )
    op.create_index("ix_bets_event_id", "bets", ["event_id"])
    op.create_index("ix_bets_status", "bets", ["status"])


def downgrade() -> None:
    op.drop_index("ix_bets_status", table_name="bets")
    op.drop_index("ix_bets_event_id", table_name="bets")
    op.drop_table("bets")
