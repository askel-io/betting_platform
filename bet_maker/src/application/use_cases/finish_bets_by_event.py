from bet_maker.src.domain.entities.bet import Bet
from bet_maker.src.domain.repositories.bet_repository import BetRepository


class FinishBetsByEventUseCase:
    def __init__(self, repository: BetRepository) -> None:
        self._repository = repository

    async def execute(self, event_id: str, event_state: str) -> list[Bet]:
        bets = await self._repository.list_pending_by_event_id(event_id)
        finished: list[Bet] = []

        for bet in bets:
            bet.finish(event_state)
            await self._repository.save(bet)
            finished.append(bet)

        return finished
