from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bet_maker.src.domain.entities.bet import Bet, BetStatus
from bet_maker.src.domain.repositories.bet_repository import BetRepository
from bet_maker.src.infrastructure.db.models.bet_model import BetModel


class PostgresBetRepository(BetRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, bet: Bet) -> None:
        model = self._to_model(bet)
        await self._session.merge(model)
        await self._session.commit()

    async def get_by_id(self, bet_id: str) -> Bet | None:
        result = await self._session.execute(
            select(BetModel).where(BetModel.bet_id == bet_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self) -> list[Bet]:
        result = await self._session.execute(select(BetModel))
        return [self._to_entity(model) for model in result.scalars().all()]

    async def list_pending(self) -> list[Bet]:
        result = await self._session.execute(
            select(BetModel).where(BetModel.status == BetStatus.PENDING.value)
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def list_pending_by_event_id(self, event_id: str) -> list[Bet]:
        result = await self._session.execute(
            select(BetModel).where(
                BetModel.event_id == event_id,
                BetModel.status == BetStatus.PENDING.value,
            )
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    @staticmethod
    def _to_model(bet: Bet) -> BetModel:
        return BetModel(
            bet_id=bet.bet_id,
            event_id=bet.event_id,
            amount=bet.amount,
            status=bet.status.value,
            created_at=bet.created_at,
            finished_at=bet.finished_at,
        )

    @staticmethod
    def _to_entity(model: BetModel) -> Bet:
        return Bet(
            bet_id=model.bet_id,
            event_id=model.event_id,
            amount=model.amount,
            status=BetStatus(model.status),
            created_at=model.created_at,
            finished_at=model.finished_at,
        )
