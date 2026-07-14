from decimal import Decimal

from bet_maker.src.domain.entities.bet import Bet
from bet_maker.src.domain.repositories.bet_repository import BetRepository


class PlaceBetUseCase:
    def __init__(self, repository: BetRepository) -> None:
        self._repository = repository

    async def execute(self, event_id: str, amount: Decimal) -> Bet:
        bet = Bet.create(event_id=event_id, amount=amount)
        await self._repository.save(bet)
        return bet
