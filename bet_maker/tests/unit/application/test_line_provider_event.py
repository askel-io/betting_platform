from datetime import datetime, timezone
from decimal import Decimal

import pytest

from bet_maker.src.application.dto.line_provider_event import LineProviderEventDTO


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def test_is_available_for_betting_when_event_is_new(now: datetime) -> None:
    event = LineProviderEventDTO(
        event_id="event-1",
        coefficient=Decimal("2.50"),
        deadline=datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc),
        state="new",
        created_at=now,
    )

    assert event.is_available_for_betting(now) is True


def test_is_not_available_when_event_is_finished(now: datetime) -> None:
    event = LineProviderEventDTO(
        event_id="event-1",
        coefficient=Decimal("2.50"),
        deadline=datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc),
        state="finished_win",
        created_at=now,
    )

    assert event.is_available_for_betting(now) is False


def test_is_not_available_when_deadline_passed(now: datetime) -> None:
    deadline = datetime(2026, 7, 14, 10, 0, tzinfo=timezone.utc)
    event = LineProviderEventDTO(
        event_id="event-1",
        coefficient=Decimal("2.50"),
        deadline=deadline,
        state="new",
        created_at=now,
    )

    assert event.is_available_for_betting(now) is False
