from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from line_provider.src.domain.entities.event import Event, EventState


class CreateEventRequest(BaseModel):
    coefficient: Decimal = Field(gt=0, decimal_places=2)
    deadline: datetime


class UpdateEventRequest(BaseModel):
    coefficient: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    deadline: datetime | None = None

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "UpdateEventRequest":
        if self.coefficient is None and self.deadline is None:
            raise ValueError("At least one field must be provided")
        return self


class EventResponse(BaseModel):
    eventId: str
    coefficient: Decimal
    deadline: datetime
    state: EventState
    created_at: datetime

    @classmethod
    def from_entity(cls, event: Event) -> "EventResponse":
        return cls(
            eventId=event.eventId,
            coefficient=event.coefficient,
            deadline=event.deadline,
            state=event.state,
            created_at=event.created_at,
        )
