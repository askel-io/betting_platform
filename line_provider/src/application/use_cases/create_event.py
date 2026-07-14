from datetime import datetime
from decimal import Decimal

from line_provider.src.domain.entities.event import Event
from line_provider.src.domain.repositories.event_repository import EventRepository


class CreateEventUseCase:
    def __init__(self, repository: EventRepository) -> None:
        self._repository = repository

    async def execute(self, coefficient: Decimal, deadline: datetime) -> Event:
        event = Event.create(coefficient=coefficient, deadline=deadline)
        await self._repository.save(event)
        return event
