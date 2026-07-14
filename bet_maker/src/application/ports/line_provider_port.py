from abc import ABC, abstractmethod

from bet_maker.src.application.dto.line_provider_event import LineProviderEventDTO


class LineProviderPort(ABC):
    @abstractmethod
    async def get_event(self, event_id: str) -> LineProviderEventDTO | None:
        raise NotImplementedError
