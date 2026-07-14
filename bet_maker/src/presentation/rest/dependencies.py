from typing import Annotated

from fastapi import Depends

from bet_maker.src.application.use_cases.finish_bet import FinishBetUseCase
from bet_maker.src.application.use_cases.get_bet import GetBetUseCase
from bet_maker.src.application.use_cases.list_bets import ListBetsUseCase
from bet_maker.src.application.use_cases.place_bet import PlaceBetUseCase
from bet_maker.src.domain.repositories.bet_repository import BetRepository
from bet_maker.src.infrastructure.db.session import get_session
from bet_maker.src.infrastructure.repositories.postgres_bet_repository import (
    PostgresBetRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession


async def get_bet_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BetRepository:
    return PostgresBetRepository(session)


def get_place_bet_use_case(
    repository: Annotated[BetRepository, Depends(get_bet_repository)],
) -> PlaceBetUseCase:
    return PlaceBetUseCase(repository)


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
