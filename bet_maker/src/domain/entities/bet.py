from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from uuid import uuid4

from bet_maker.src.errors.bet_error import InvalidAmountError


class BetStatus(Enum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"


FINISHED_WIN = "finished_win"
FINISHED_LOSE = "finished_lose"


def _to_amount(value: Decimal) -> Decimal:
    try:
        amount = Decimal(value).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        raise InvalidAmountError(value)

    if amount <= 0:
        raise InvalidAmountError(value)

    return amount


@dataclass
class Bet:
    event_id: str
    amount: Decimal
    bet_id: str = field(default_factory=lambda: str(uuid4()))
    status: BetStatus = BetStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None

    @classmethod
    def create(cls, event_id: str, amount: Decimal) -> "Bet":
        return cls(
            event_id=event_id,
            amount=_to_amount(amount),
        )

    def finish(self, event_state: str, finished_at: datetime | None = None) -> None:
        if self.status != BetStatus.PENDING:
            return

        finished_at = finished_at or datetime.now(timezone.utc)

        if event_state == FINISHED_WIN:
            self.status = BetStatus.WON
        elif event_state == FINISHED_LOSE:
            self.status = BetStatus.LOST
        else:
            raise ValueError(f"Unsupported event state: {event_state}")

        self.finished_at = finished_at
