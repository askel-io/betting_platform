from decimal import Decimal

import pytest

from line_provider.src.application.use_cases.create_event import CreateEventUseCase
from line_provider.src.application.use_cases.get_event import GetEventUseCase
from line_provider.src.application.use_cases.list_events import ListEventsUseCase
from line_provider.src.application.use_cases.update_event import UpdateEventUseCase
from line_provider.src.domain.entities.event import EventState
from line_provider.src.errors.event_error import EventNotFoundError
from line_provider.src.infrastructure.repositories.postgres_event_repository import (
    PostgresEventRepository,
)


@pytest.mark.asyncio
async def test_create_event_use_case(
    event_repository: PostgresEventRepository,
    coefficient: Decimal,
    future_deadline,
) -> None:
    use_case = CreateEventUseCase(event_repository)

    event = await use_case.execute(coefficient, future_deadline)

    saved = await event_repository.get_by_id(event.event_id)
    assert saved is not None
    assert saved.coefficient == Decimal("2.50")


@pytest.mark.asyncio
async def test_get_event_not_found(
    event_repository: PostgresEventRepository,
) -> None:
    use_case = GetEventUseCase(event_repository)

    with pytest.raises(EventNotFoundError):
        await use_case.execute("missing-id")


@pytest.mark.asyncio
async def test_list_events_use_case(
    event_repository: PostgresEventRepository,
    coefficient: Decimal,
    future_deadline,
) -> None:
    create_use_case = CreateEventUseCase(event_repository)
    list_use_case = ListEventsUseCase(event_repository)

    await create_use_case.execute(coefficient, future_deadline)
    await create_use_case.execute(Decimal("3.00"), future_deadline)

    events = await list_use_case.execute()

    assert len(events) == 2


@pytest.mark.asyncio
async def test_update_event_use_case(
    event_repository: PostgresEventRepository,
    coefficient: Decimal,
    future_deadline,
    now,
) -> None:
    create_use_case = CreateEventUseCase(event_repository)
    update_use_case = UpdateEventUseCase(event_repository)

    event = await create_use_case.execute(coefficient, future_deadline)
    updated = await update_use_case.execute(
        event_id=event.event_id,
        coefficient=Decimal("5.00"),
        now=now,
    )

    assert updated.coefficient == Decimal("5.00")

    saved = await event_repository.get_by_id(event.event_id)
    assert saved is not None
    assert saved.coefficient == Decimal("5.00")


@pytest.mark.asyncio
async def test_update_event_not_found(
    event_repository: PostgresEventRepository,
    now,
) -> None:
    use_case = UpdateEventUseCase(event_repository)

    with pytest.raises(EventNotFoundError):
        await use_case.execute(
            event_id="missing-id",
            coefficient=Decimal("5.00"),
            now=now,
        )
