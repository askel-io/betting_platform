from typing import Annotated

from fastapi import APIRouter, Depends, status

from bet_maker.src.application.use_cases.finish_bet import FinishBetUseCase
from bet_maker.src.application.use_cases.get_bet import GetBetUseCase
from bet_maker.src.application.use_cases.list_bets import ListBetsUseCase
from bet_maker.src.application.use_cases.place_bet import PlaceBetUseCase
from bet_maker.src.presentation.rest.dependencies import (
    get_finish_bet_use_case,
    get_get_bet_use_case,
    get_list_bets_use_case,
    get_place_bet_use_case,
)
from bet_maker.src.presentation.rest.schemas.bet import (
    BetResponse,
    FinishBetRequest,
    PlaceBetRequest,
    PlaceBetResponse,
)

router = APIRouter(tags=["bets"])


@router.post("/bet", response_model=PlaceBetResponse, status_code=status.HTTP_201_CREATED)
async def place_bet(
    body: PlaceBetRequest,
    use_case: Annotated[PlaceBetUseCase, Depends(get_place_bet_use_case)],
) -> PlaceBetResponse:
    bet = await use_case.execute(
        event_id=body.event_id,
        amount=body.amount,
    )
    return PlaceBetResponse(bet_id=bet.bet_id)


@router.get("/bets", response_model=list[BetResponse])
async def list_bets(
    use_case: Annotated[ListBetsUseCase, Depends(get_list_bets_use_case)],
) -> list[BetResponse]:
    bets = await use_case.execute()
    return [BetResponse.from_entity(bet) for bet in bets]


@router.get("/bets/{bet_id}", response_model=BetResponse)
async def get_bet(
    bet_id: str,
    use_case: Annotated[GetBetUseCase, Depends(get_get_bet_use_case)],
) -> BetResponse:
    bet = await use_case.execute(bet_id)
    return BetResponse.from_entity(bet)


@router.patch("/bets/{bet_id}/finish", response_model=BetResponse)
async def finish_bet(
    bet_id: str,
    body: FinishBetRequest,
    use_case: Annotated[FinishBetUseCase, Depends(get_finish_bet_use_case)],
) -> BetResponse:
    bet = await use_case.execute(bet_id=bet_id, event_state=body.state)
    return BetResponse.from_entity(bet)
