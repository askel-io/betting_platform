from datetime import datetime, timezone
from decimal import Decimal

from bet_maker.src.application.ports.line_provider_port import LineProviderPort
from bet_maker.src.domain.entities.bet import Bet
from bet_maker.src.domain.repositories.bet_repository import BetRepository
from bet_maker.src.errors.bet_error import EventNotAvailableError, EventNotFoundError


class PlaceBetUseCase:
    def __init__(
        self,
        repository: BetRepository,
        line_provider: LineProviderPort,
    ) -> None:
        self._repository = repository
        self._line_provider = line_provider

    async def execute(
        self,
        event_id: str,
        amount: Decimal,
        now: datetime | None = None,
    ) -> Bet:
        now = now or datetime.now(timezone.utc)

        event = await self._line_provider.get_event(event_id)
        if event is None:
            raise EventNotFoundError(event_id)
        if not event.is_available_for_betting(now):
            raise EventNotAvailableError(event_id)

        bet = Bet.create(event_id=event_id, amount=amount)
        await self._repository.save(bet)
        return bet
