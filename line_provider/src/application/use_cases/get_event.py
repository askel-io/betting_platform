from line_provider.src.domain.entities.event import Event
from line_provider.src.domain.repositories.event_repository import EventRepository
from line_provider.src.errors.event_error import EventNotFoundError


class GetEventUseCase:
    def __init__(self, repository: EventRepository) -> None:
        self._repository = repository

    async def execute(self, event_id: str) -> Event:
        event = await self._repository.get_by_id(event_id)
        if event is None:
            raise EventNotFoundError(event_id)
        return event
