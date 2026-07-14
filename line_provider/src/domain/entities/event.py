from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from uuid import uuid4

from line_provider.src.errors.event_error import (
    EventAlreadyFinishedError,
    EventNotEditableError,
    InvalidCoefficientError,
    InvalidDeadlineError,
)


class EventState(Enum):
    NEW = "new"
    FINISHED_WIN = "finished_win"
    FINISHED_LOSE = "finished_lose"


def _to_coefficient(value: Decimal) -> Decimal:
    try:
        coefficient = Decimal(value).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        raise InvalidCoefficientError(value)

    if coefficient <= 0:
        raise InvalidCoefficientError(value)

    return coefficient


@dataclass
class Event:
    coefficient: Decimal
    deadline: datetime
    event_id: str = field(default_factory=lambda: str(uuid4()))
    state: EventState = EventState.NEW
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        coefficient: Decimal,
        deadline: datetime,
        now: datetime | None = None,
    ) -> "Event":
        now = now or datetime.now(timezone.utc)
        coefficient = _to_coefficient(coefficient)

        if deadline.tzinfo is None:
            raise InvalidDeadlineError("Deadline must be timezone-aware")

        if deadline <= now:
            raise InvalidDeadlineError("Deadline must be in the future")

        return cls(coefficient=coefficient, deadline=deadline, created_at=now)

    def is_open_for_betting(self, now: datetime) -> bool:
        return self.state == EventState.NEW and now < self.deadline

    def update_coefficient(self, coefficient: Decimal) -> None:
        self._ensure_editable()
        self.coefficient = _to_coefficient(coefficient)

    def update_deadline(self, deadline: datetime, now: datetime) -> None:
        self._ensure_editable()

        if deadline.tzinfo is None:
            raise InvalidDeadlineError("Deadline must be timezone-aware")

        if deadline <= now:
            raise InvalidDeadlineError("Deadline must be in the future")

        self.deadline = deadline

    def finish_win(self) -> None:
        self._finish(EventState.FINISHED_WIN)

    def finish_lose(self) -> None:
        self._finish(EventState.FINISHED_LOSE)

    def _finish(self, new_state: EventState) -> None:
        if self.state != EventState.NEW:
            raise EventAlreadyFinishedError(self.event_id)
        self.state = new_state

    def _ensure_editable(self) -> None:
        if self.state != EventState.NEW:
            raise EventNotEditableError(self.event_id)
