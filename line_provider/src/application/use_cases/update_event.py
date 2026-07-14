from datetime import datetime, timezone
from decimal import Decimal

from line_provider.src.domain.entities.event import Event
from line_provider.src.domain.repositories.event_repository import EventRepository
from line_provider.src.errors.event_error import EventNotFoundError


class UpdateEventUseCase:
    def __init__(self, repository: EventRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        event_id: str,
        coefficient: Decimal | None = None,
        deadline: datetime | None = None,
        now: datetime | None = None,
    ) -> Event:
        event = await self._repository.get_by_id(event_id)
        if event is None:
            raise EventNotFoundError(event_id)

        now = now or datetime.now(timezone.utc)

        if coefficient is not None:
            event.update_coefficient(coefficient)

        if deadline is not None:
            event.update_deadline(deadline, now)

        await self._repository.save(event)
        return event
