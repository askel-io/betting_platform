from abc import ABC, abstractmethod

from line_provider.src.domain.entities.event import Event


class EventRepository(ABC):
    @abstractmethod
    async def save(self, event: Event) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, event_id: str) -> Event | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[Event]:
        raise NotImplementedError
