from decimal import Decimal

import pytest

from bet_maker.src.domain.entities.bet import FINISHED_WIN, Bet, BetStatus
from bet_maker.src.infrastructure.repositories.postgres_bet_repository import (
    PostgresBetRepository,
)


@pytest.mark.asyncio
async def test_save_and_get(
    bet_repository: PostgresBetRepository,
    event_id: str,
    amount: Decimal,
) -> None:
    bet = Bet.create(event_id=event_id, amount=amount)

    await bet_repository.save(bet)
    loaded = await bet_repository.get_by_id(bet.bet_id)

    assert loaded is not None
    assert loaded.bet_id == bet.bet_id
    assert loaded.event_id == event_id
    assert loaded.amount == amount
    assert loaded.status == BetStatus.PENDING


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing(
    bet_repository: PostgresBetRepository,
) -> None:
    loaded = await bet_repository.get_by_id("missing-id")

    assert loaded is None


@pytest.mark.asyncio
async def test_list_all(
    bet_repository: PostgresBetRepository,
    event_id: str,
    amount: Decimal,
) -> None:
    bet1 = Bet.create(event_id=event_id, amount=amount)
    bet2 = Bet.create(event_id="event-456", amount=Decimal("50.00"))

    await bet_repository.save(bet1)
    await bet_repository.save(bet2)

    bets = await bet_repository.list_all()

    assert len(bets) == 2
    bet_ids = {bet.bet_id for bet in bets}
    assert bet1.bet_id in bet_ids
    assert bet2.bet_id in bet_ids


@pytest.mark.asyncio
async def test_list_pending(
    bet_repository: PostgresBetRepository,
    event_id: str,
    amount: Decimal,
    now,
) -> None:
    pending_bet = Bet.create(event_id=event_id, amount=amount)
    finished_bet = Bet.create(event_id=event_id, amount=Decimal("25.00"))
    finished_bet.finish(FINISHED_WIN, finished_at=now)

    await bet_repository.save(pending_bet)
    await bet_repository.save(finished_bet)

    pending_bets = await bet_repository.list_pending()

    assert len(pending_bets) == 1
    assert pending_bets[0].bet_id == pending_bet.bet_id


@pytest.mark.asyncio
async def test_list_pending_by_event_id(
    bet_repository: PostgresBetRepository,
    event_id: str,
    amount: Decimal,
    now,
) -> None:
    target_bet = Bet.create(event_id=event_id, amount=amount)
    other_event_bet = Bet.create(event_id="other-event", amount=Decimal("25.00"))
    finished_bet = Bet.create(event_id=event_id, amount=Decimal("10.00"))
    finished_bet.finish(FINISHED_WIN, finished_at=now)

    await bet_repository.save(target_bet)
    await bet_repository.save(other_event_bet)
    await bet_repository.save(finished_bet)

    pending_bets = await bet_repository.list_pending_by_event_id(event_id)

    assert len(pending_bets) == 1
    assert pending_bets[0].bet_id == target_bet.bet_id


@pytest.mark.asyncio
async def test_save_updates_existing_bet(
    bet_repository: PostgresBetRepository,
    event_id: str,
    amount: Decimal,
    now,
) -> None:
    bet = Bet.create(event_id=event_id, amount=amount)
    await bet_repository.save(bet)

    bet.finish(FINISHED_WIN, finished_at=now)
    await bet_repository.save(bet)

    loaded = await bet_repository.get_by_id(bet.bet_id)

    assert loaded is not None
    assert loaded.status == BetStatus.WON
    assert loaded.finished_at == now
