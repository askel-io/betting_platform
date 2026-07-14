from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from line_provider.src.application.use_cases.create_event import CreateEventUseCase
from line_provider.src.application.use_cases.finish_event import FinishEventUseCase
from line_provider.src.application.use_cases.get_event import GetEventUseCase
from line_provider.src.application.use_cases.list_events import ListEventsUseCase
from line_provider.src.application.use_cases.update_event import UpdateEventUseCase
from line_provider.src.domain.repositories.event_repository import EventRepository
from line_provider.src.infrastructure.db.session import get_session
from line_provider.src.infrastructure.messaging.publisher_registry import (
    get_event_finished_publisher,
)
from line_provider.src.infrastructure.repositories.postgres_event_repository import (
    PostgresEventRepository,
)


async def get_event_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EventRepository:
    return PostgresEventRepository(session)


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


def get_finish_event_use_case(
    repository: Annotated[EventRepository, Depends(get_event_repository)],
) -> FinishEventUseCase:
    return FinishEventUseCase(repository, get_event_finished_publisher())
