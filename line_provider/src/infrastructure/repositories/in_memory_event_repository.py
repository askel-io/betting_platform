from line_provider.src.domain.entities.event import Event
from line_provider.src.domain.repositories.event_repository import EventRepository


class InMemoryEventRepository(EventRepository):
    def __init__(self) -> None:
        self._storage: dict[str, Event] = {}

    async def save(self, event: Event) -> None:
        self._storage[event.eventId] = event

    async def get_by_id(self, event_id: str) -> Event | None:
        return self._storage.get(event_id)

    async def list_all(self) -> list[Event]:
        return list(self._storage.values())
