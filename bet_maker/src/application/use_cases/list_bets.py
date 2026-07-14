from bet_maker.src.domain.entities.bet import Bet
from bet_maker.src.domain.repositories.bet_repository import BetRepository


class ListBetsUseCase:
    def __init__(self, repository: BetRepository) -> None:
        self._repository = repository

    async def execute(self) -> list[Bet]:
        return await self._repository.list_all()
