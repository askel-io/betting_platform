import httpx

from bet_maker.src.application.dto.line_provider_event import LineProviderEventDTO
from bet_maker.src.application.ports.line_provider_port import LineProviderPort


class LineProviderClient(LineProviderPort):
    def __init__(self, base_url: str, client: httpx.AsyncClient) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = client

    async def get_event(self, event_id: str) -> LineProviderEventDTO | None:
        response = await self._client.get(
            f"{self._base_url}/rest/api/v1/events/{event_id}",
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return LineProviderEventDTO.model_validate(response.json())
