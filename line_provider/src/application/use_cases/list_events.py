from line_provider.src.domain.entities.event import Event
from line_provider.src.domain.repositories.event_repository import EventRepository


class ListEventsUseCase:
    def __init__(self, repository: EventRepository) -> None:
        self._repository = repository

    async def execute(self) -> list[Event]:
        return await self._repository.list_all()
