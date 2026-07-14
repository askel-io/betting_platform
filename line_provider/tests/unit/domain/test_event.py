import pytest

from datetime import datetime, timezone
from decimal import Decimal

from line_provider.src.domain.entities.event import Event, EventState
from line_provider.src.errors.event_error import (
    EventAlreadyFinishedError,
    EventNotEditableError,
    InvalidCoefficientError,
    InvalidDeadlineError,
)


def test_create_event_success(now: datetime, future_deadline: datetime) -> None:
    event = Event.create(
        coefficient=Decimal("2.50"),
        deadline=future_deadline,
        now=now,
    )

    assert event.state == EventState.NEW
    assert event.coefficient == Decimal("2.50")
    assert event.created_at == now


def test_create_event_with_past_deadline_fails(now: datetime) -> None:
    with pytest.raises(InvalidDeadlineError):
        Event.create(
            coefficient=Decimal("2.50"),
            deadline=now,
            now=now,
        )


def test_create_event_without_timezone_fails(now: datetime) -> None:
    naive_deadline = datetime(2026, 7, 15, 18, 0)

    with pytest.raises(InvalidDeadlineError):
        Event.create(
            coefficient=Decimal("2.50"),
            deadline=naive_deadline,
            now=now,
        )


def test_invalid_coefficient_fails(now: datetime, future_deadline: datetime) -> None:
    with pytest.raises(InvalidCoefficientError):
        Event.create(
            coefficient=Decimal("-1.00"),
            deadline=future_deadline,
            now=now,
        )


def test_is_open_for_betting(now: datetime, future_deadline: datetime) -> None:
    event = Event.create(Decimal("2.50"), future_deadline, now=now)

    assert event.is_open_for_betting(now) is True
    assert event.is_open_for_betting(future_deadline) is False


def test_update_coefficient_success(now: datetime, future_deadline: datetime) -> None:
    event = Event.create(Decimal("2.50"), future_deadline, now=now)

    event.update_coefficient(Decimal("3.75"))

    assert event.coefficient == Decimal("3.75")


def test_update_coefficient_on_finished_event_fails(
    now: datetime,
    future_deadline: datetime,
) -> None:
    event = Event.create(Decimal("2.50"), future_deadline, now=now)
    event.finish_win()

    with pytest.raises(EventNotEditableError):
        event.update_coefficient(Decimal("3.00"))


def test_finish_event_twice_fails(now: datetime, future_deadline: datetime) -> None:
    event = Event.create(Decimal("2.50"), future_deadline, now=now)
    event.finish_win()

    with pytest.raises(EventAlreadyFinishedError):
        event.finish_lose()


def test_update_deadline_success(now: datetime, future_deadline: datetime) -> None:
    event = Event.create(Decimal("2.50"), future_deadline, now=now)
    new_deadline = datetime(2026, 7, 20, 18, 0, tzinfo=timezone.utc)

    event.update_deadline(new_deadline, now)

    assert event.deadline == new_deadline
