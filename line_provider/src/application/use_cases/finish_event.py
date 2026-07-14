from typing import Literal

from line_provider.src.application.ports.event_finished_publisher import EventFinishedPublisher
from line_provider.src.domain.entities.event import Event
from line_provider.src.domain.repositories.event_repository import EventRepository
from line_provider.src.errors.event_error import EventNotFoundError


class FinishEventUseCase:
    def __init__(
        self,
        repository: EventRepository,
        publisher: EventFinishedPublisher,
    ) -> None:
        self._repository = repository
        self._publisher = publisher

    async def execute(
        self,
        event_id: str,
        state: Literal["finished_win", "finished_lose"],
    ) -> Event:
        event = await self._repository.get_by_id(event_id)
        if event is None:
            raise EventNotFoundError(event_id)

        if state == "finished_win":
            event.finish_win()
        else:
            event.finish_lose()

        await self._repository.save(event)
        await self._publisher.publish(event_id=event.event_id, state=state)
        return event
