from abc import ABC, abstractmethod


class EventFinishedPublisher(ABC):
    @abstractmethod
    async def publish(self, event_id: str, state: str) -> None:
        raise NotImplementedError
