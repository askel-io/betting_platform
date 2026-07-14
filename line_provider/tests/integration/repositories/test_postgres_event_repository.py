from decimal import Decimal

import pytest

from line_provider.src.domain.entities.event import Event
from line_provider.src.infrastructure.repositories.postgres_event_repository import (
    PostgresEventRepository,
)


@pytest.mark.asyncio
async def test_save_and_get(
    event_repository: PostgresEventRepository,
    coefficient: Decimal,
    future_deadline,
    now,
) -> None:
    event = Event.create(coefficient, future_deadline, now=now)

    await event_repository.save(event)
    loaded = await event_repository.get_by_id(event.event_id)

    assert loaded is not None
    assert loaded.event_id == event.event_id
    assert loaded.coefficient == event.coefficient
    assert loaded.deadline == event.deadline


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing(
    event_repository: PostgresEventRepository,
) -> None:
    loaded = await event_repository.get_by_id("missing-id")

    assert loaded is None


@pytest.mark.asyncio
async def test_list_all(
    event_repository: PostgresEventRepository,
    coefficient: Decimal,
    future_deadline,
    now,
) -> None:
    event1 = Event.create(coefficient, future_deadline, now=now)
    event2 = Event.create(Decimal("3.00"), future_deadline, now=now)

    await event_repository.save(event1)
    await event_repository.save(event2)

    events = await event_repository.list_all()

    assert len(events) == 2
    event_ids = {event.event_id for event in events}
    assert event1.event_id in event_ids
    assert event2.event_id in event_ids


@pytest.mark.asyncio
async def test_save_updates_existing_event(
    event_repository: PostgresEventRepository,
    coefficient: Decimal,
    future_deadline,
    now,
) -> None:
    event = Event.create(coefficient, future_deadline, now=now)
    await event_repository.save(event)

    event.update_coefficient(Decimal("4.50"))
    await event_repository.save(event)

    loaded = await event_repository.get_by_id(event.event_id)

    assert loaded is not None
    assert loaded.coefficient == Decimal("4.50")
