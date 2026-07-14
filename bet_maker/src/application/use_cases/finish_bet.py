from bet_maker.src.domain.entities.bet import Bet
from bet_maker.src.domain.repositories.bet_repository import BetRepository
from bet_maker.src.errors.bet_error import BetNotFoundError


class FinishBetUseCase:
    def __init__(self, repository: BetRepository) -> None:
        self._repository = repository

    async def execute(self, bet_id: str, event_state: str) -> Bet:
        bet = await self._repository.get_by_id(bet_id)
        if bet is None:
            raise BetNotFoundError(bet_id)

        bet.finish(event_state)
        await self._repository.save(bet)
        return bet
