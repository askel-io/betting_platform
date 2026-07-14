from typing import Annotated

from fastapi import Depends

from line_provider.src.application.use_cases.create_event import CreateEventUseCase
from line_provider.src.application.use_cases.get_event import GetEventUseCase
from line_provider.src.application.use_cases.list_events import ListEventsUseCase
from line_provider.src.application.use_cases.update_event import UpdateEventUseCase
from line_provider.src.domain.repositories.event_repository import EventRepository
from line_provider.src.infrastructure.repositories.in_memory_event_repository import (
    InMemoryEventRepository,
)

_repository: EventRepository | None = None


def get_event_repository() -> EventRepository:
    global _repository
    if _repository is None:
        _repository = InMemoryEventRepository()
    return _repository


def get_create_event_use_case(
    repository: Annotated[EventRepository, Depends(get_event_repository)],
) -> CreateEventUseCase:
    return CreateEventUseCase(repository)


def get_get_event_use_case(
    repository: Annotated[EventRepository, Depends(get_event_repository)],
) -> GetEventUseCase:
    return GetEventUseCase(repository)


def get_list_events_use_case(
    repository: Annotated[EventRepository, Depends(get_event_repository)],
) -> ListEventsUseCase:
    return ListEventsUseCase(repository)


def get_update_event_use_case(
    repository: Annotated[EventRepository, Depends(get_event_repository)],
) -> UpdateEventUseCase:
    return UpdateEventUseCase(repository)
