from typing import Annotated

import httpx
from fastapi import Depends

from bet_maker.src.application.ports.line_provider_port import LineProviderPort
from bet_maker.src.application.use_cases.finish_bet import FinishBetUseCase
from bet_maker.src.application.use_cases.get_bet import GetBetUseCase
from bet_maker.src.application.use_cases.list_bets import ListBetsUseCase
from bet_maker.src.application.use_cases.place_bet import PlaceBetUseCase
from bet_maker.src.domain.repositories.bet_repository import BetRepository
from bet_maker.src.infrastructure.clients.line_provider_client import LineProviderClient
from bet_maker.src.infrastructure.config import LINE_PROVIDER_URL
from bet_maker.src.infrastructure.db.session import get_session
from bet_maker.src.infrastructure.repositories.postgres_bet_repository import (
    PostgresBetRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession

_http_client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=10.0)
    return _http_client


async def close_http_client() -> None:
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


def get_line_provider(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> LineProviderPort:
    return LineProviderClient(LINE_PROVIDER_URL, client)


async def get_bet_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BetRepository:
    return PostgresBetRepository(session)


def get_place_bet_use_case(
    repository: Annotated[BetRepository, Depends(get_bet_repository)],
    line_provider: Annotated[LineProviderPort, Depends(get_line_provider)],
) -> PlaceBetUseCase:
    return PlaceBetUseCase(repository, line_provider)


def get_list_bets_use_case(
    repository: Annotated[BetRepository, Depends(get_bet_repository)],
) -> ListBetsUseCase:
    return ListBetsUseCase(repository)


def get_get_bet_use_case(
    repository: Annotated[BetRepository, Depends(get_bet_repository)],
) -> GetBetUseCase:
    return GetBetUseCase(repository)


def get_finish_bet_use_case(
    repository: Annotated[BetRepository, Depends(get_bet_repository)],
) -> FinishBetUseCase:
    return FinishBetUseCase(repository)
