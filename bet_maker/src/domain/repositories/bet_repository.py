from abc import ABC, abstractmethod

from bet_maker.src.domain.entities.bet import Bet


class BetRepository(ABC):
    @abstractmethod
    async def save(self, bet: Bet) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, bet_id: str) -> Bet | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[Bet]:
        raise NotImplementedError

    @abstractmethod
    async def list_pending(self) -> list[Bet]:
        raise NotImplementedError

    @abstractmethod
    async def list_pending_by_event_id(self, event_id: str) -> list[Bet]:
        raise NotImplementedError
