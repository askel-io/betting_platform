from typing import Annotated

from fastapi import APIRouter, Depends, status

from line_provider.src.application.use_cases.create_event import CreateEventUseCase
from line_provider.src.application.use_cases.finish_event import FinishEventUseCase
from line_provider.src.application.use_cases.get_event import GetEventUseCase
from line_provider.src.application.use_cases.list_events import ListEventsUseCase
from line_provider.src.application.use_cases.update_event import UpdateEventUseCase
from line_provider.src.presentation.rest.dependencies import (
    get_create_event_use_case,
    get_finish_event_use_case,
    get_get_event_use_case,
    get_list_events_use_case,
    get_update_event_use_case,
)
from line_provider.src.presentation.rest.schemas.event import (
    CreateEventRequest,
    EventResponse,
    FinishEventRequest,
    UpdateEventRequest,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    body: CreateEventRequest,
    use_case: Annotated[CreateEventUseCase, Depends(get_create_event_use_case)],
) -> EventResponse:
    event = await use_case.execute(
        coefficient=body.coefficient,
        deadline=body.deadline,
    )
    return EventResponse.from_entity(event)


@router.get("", response_model=list[EventResponse])
async def list_events(
    use_case: Annotated[ListEventsUseCase, Depends(get_list_events_use_case)],
) -> list[EventResponse]:
    events = await use_case.execute()
    return [EventResponse.from_entity(event) for event in events]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    use_case: Annotated[GetEventUseCase, Depends(get_get_event_use_case)],
) -> EventResponse:
    event = await use_case.execute(event_id)
    return EventResponse.from_entity(event)


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    body: UpdateEventRequest,
    use_case: Annotated[UpdateEventUseCase, Depends(get_update_event_use_case)],
) -> EventResponse:
    event = await use_case.execute(
        event_id=event_id,
        coefficient=body.coefficient,
        deadline=body.deadline,
    )
    return EventResponse.from_entity(event)


@router.patch("/{event_id}/finish", response_model=EventResponse)
async def finish_event(
    event_id: str,
    body: FinishEventRequest,
    use_case: Annotated[FinishEventUseCase, Depends(get_finish_event_use_case)],
) -> EventResponse:
    event = await use_case.execute(event_id=event_id, state=body.state)
    return EventResponse.from_entity(event)
