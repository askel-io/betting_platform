# infrastructure/repositories/postgres_event_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from line_provider.src.domain.entities.event import Event, EventState
from line_provider.src.domain.repositories.event_repository import EventRepository
from line_provider.src.infrastructure.db.models.event_model import EventModel


class PostgresEventRepository(EventRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, event: Event) -> None:
        model = self._to_model(event)
        await self._session.merge(model)
        await self._session.commit()

    async def get_by_id(self, event_id: str) -> Event | None:
        result = await self._session.execute(
            select(EventModel).where(EventModel.event_id == event_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self) -> list[Event]:
        result = await self._session.execute(select(EventModel))
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_model(event: Event) -> EventModel:
        return EventModel(
            event_id=event.event_id,
            coefficient=event.coefficient,
            deadline=event.deadline,
            state=event.state.value,
            created_at=event.created_at,
        )

    @staticmethod
    def _to_entity(model: EventModel) -> Event:
        return Event(
            event_id=model.event_id,
            coefficient=model.coefficient,
            deadline=model.deadline,
            state=EventState(model.state),
            created_at=model.created_at,
        )