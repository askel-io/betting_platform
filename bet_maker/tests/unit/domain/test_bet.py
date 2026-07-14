import pytest

from datetime import datetime, timezone
from decimal import Decimal

from bet_maker.src.domain.entities.bet import Bet, BetStatus, FINISHED_LOSE, FINISHED_WIN
from bet_maker.src.errors.bet_error import InvalidAmountError


def test_create_bet_success(event_id: str, amount: Decimal) -> None:
    bet = Bet.create(event_id=event_id, amount=amount)

    assert bet.event_id == event_id
    assert bet.amount == amount
    assert bet.status == BetStatus.PENDING
    assert bet.finished_at is None


@pytest.mark.parametrize("invalid_amount", [Decimal("0"), Decimal("-10.00")])
def test_create_bet_with_invalid_amount_fails(
    event_id: str,
    invalid_amount: Decimal,
) -> None:
    with pytest.raises(InvalidAmountError):
        Bet.create(event_id=event_id, amount=invalid_amount)


def test_finish_bet_win(event_id: str, amount: Decimal, now: datetime) -> None:
    bet = Bet.create(event_id=event_id, amount=amount)

    bet.finish(FINISHED_WIN, finished_at=now)

    assert bet.status == BetStatus.WON
    assert bet.finished_at == now


def test_finish_bet_lose(event_id: str, amount: Decimal, now: datetime) -> None:
    bet = Bet.create(event_id=event_id, amount=amount)

    bet.finish(FINISHED_LOSE, finished_at=now)

    assert bet.status == BetStatus.LOST
    assert bet.finished_at == now


def test_finish_bet_is_idempotent(event_id: str, amount: Decimal, now: datetime) -> None:
    bet = Bet.create(event_id=event_id, amount=amount)
    bet.finish(FINISHED_WIN, finished_at=now)

    bet.finish(FINISHED_LOSE, finished_at=now)

    assert bet.status == BetStatus.WON
    assert bet.finished_at == now


def test_finish_bet_with_unsupported_state_fails(
    event_id: str,
    amount: Decimal,
) -> None:
    bet = Bet.create(event_id=event_id, amount=amount)

    with pytest.raises(ValueError, match="Unsupported event state"):
        bet.finish("unknown_state")
