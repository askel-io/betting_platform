from line_provider.src.domain.entities.event import Event, EventState
from line_provider.src.domain.repositories.event_repository import EventRepository
from line_provider.src.errors.event_error import EventNotFoundError


class UpdateEventStateUseCase:
    def __init__(self, repository: EventRepository) -> None:
        self._repository = repository

    async def execute(self, event_id: str, state: EventState) -> Event:
        event = await self._repository.get_by_id(event_id)
        if event is None:
            raise EventNotFoundError(event_id)

        if state == EventState.FINISHED_WIN:
            event.finish_win()
        elif state == EventState.FINISHED_LOSE:
            event.finish_lose()
        else:
            raise ValueError(f"Invalid state transition: {state.value}")

        await self._repository.save(event)
        return event
