from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from bet_maker.src.domain.entities.bet import Bet, BetStatus


class PlaceBetRequest(BaseModel):
    event_id: str
    amount: Decimal = Field(gt=0, decimal_places=2)


class PlaceBetResponse(BaseModel):
    bet_id: str


class FinishBetRequest(BaseModel):
    state: Literal["finished_win", "finished_lose"]


class BetResponse(BaseModel):
    bet_id: str
    event_id: str
    amount: Decimal
    status: BetStatus
    created_at: datetime
    finished_at: datetime | None

    @classmethod
    def from_entity(cls, bet: Bet) -> "BetResponse":
        return cls(
            bet_id=bet.bet_id,
            event_id=bet.event_id,
            amount=bet.amount,
            status=bet.status,
            created_at=bet.created_at,
            finished_at=bet.finished_at,
        )
