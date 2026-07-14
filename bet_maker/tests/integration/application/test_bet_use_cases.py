from decimal import Decimal

import pytest

from bet_maker.src.application.dto.line_provider_event import LineProviderEventDTO
from bet_maker.src.application.use_cases.finish_bet import FinishBetUseCase
from bet_maker.src.application.use_cases.finish_bets_by_event import (
    FinishBetsByEventUseCase,
)
from bet_maker.src.application.use_cases.get_bet import GetBetUseCase
from bet_maker.src.application.use_cases.list_bets import ListBetsUseCase
from bet_maker.src.application.use_cases.place_bet import PlaceBetUseCase
from bet_maker.src.domain.entities.bet import (
    FINISHED_LOSE,
    FINISHED_WIN,
    Bet,
    BetStatus,
)
from bet_maker.src.errors.bet_error import (
    BetNotFoundError,
    EventNotAvailableError,
    EventNotFoundError,
)
from bet_maker.src.infrastructure.repositories.postgres_bet_repository import (
    PostgresBetRepository,
)
from bet_maker.tests.conftest import FakeLineProviderPort


@pytest.mark.asyncio
async def test_place_bet_use_case_success(
    bet_repository: PostgresBetRepository,
    fake_line_provider: FakeLineProviderPort,
    event_id: str,
    amount: Decimal,
    now,
) -> None:
    use_case = PlaceBetUseCase(bet_repository, fake_line_provider)

    bet = await use_case.execute(event_id=event_id, amount=amount, now=now)

    assert bet.event_id == event_id
    assert bet.amount == amount
    assert bet.status == BetStatus.PENDING

    saved = await bet_repository.get_by_id(bet.bet_id)
    assert saved is not None


@pytest.mark.asyncio
async def test_place_bet_event_not_found(
    bet_repository: PostgresBetRepository,
    fake_line_provider: FakeLineProviderPort,
    amount: Decimal,
    now,
) -> None:
    use_case = PlaceBetUseCase(bet_repository, fake_line_provider)

    with pytest.raises(EventNotFoundError):
        await use_case.execute(event_id="missing-event", amount=amount, now=now)


@pytest.mark.asyncio
async def test_place_bet_event_not_available_when_finished(
    bet_repository: PostgresBetRepository,
    fake_line_provider: FakeLineProviderPort,
    available_event: LineProviderEventDTO,
    amount: Decimal,
    now,
) -> None:
    finished_event = available_event.model_copy(update={"state": "finished_win"})
    fake_line_provider.add_event(finished_event)

    use_case = PlaceBetUseCase(bet_repository, fake_line_provider)

    with pytest.raises(EventNotAvailableError):
        await use_case.execute(
            event_id=finished_event.event_id,
            amount=amount,
            now=now,
        )


@pytest.mark.asyncio
async def test_place_bet_event_not_available_when_deadline_passed(
    bet_repository: PostgresBetRepository,
    fake_line_provider: FakeLineProviderPort,
    available_event: LineProviderEventDTO,
    amount: Decimal,
    past_deadline,
    now,
) -> None:
    expired_event = available_event.model_copy(update={"deadline": past_deadline})
    fake_line_provider.add_event(expired_event)

    use_case = PlaceBetUseCase(bet_repository, fake_line_provider)

    with pytest.raises(EventNotAvailableError):
        await use_case.execute(
            event_id=expired_event.event_id,
            amount=amount,
            now=now,
        )


@pytest.mark.asyncio
async def test_get_bet_use_case(
    bet_repository: PostgresBetRepository,
    event_id: str,
    amount: Decimal,
) -> None:
    bet = Bet.create(event_id=event_id, amount=amount)
    await bet_repository.save(bet)

    use_case = GetBetUseCase(bet_repository)
    loaded = await use_case.execute(bet.bet_id)

    assert loaded.bet_id == bet.bet_id


@pytest.mark.asyncio
async def test_get_bet_not_found(
    bet_repository: PostgresBetRepository,
) -> None:
    use_case = GetBetUseCase(bet_repository)

    with pytest.raises(BetNotFoundError):
        await use_case.execute("missing-id")


@pytest.mark.asyncio
async def test_list_bets_use_case(
    bet_repository: PostgresBetRepository,
    event_id: str,
    amount: Decimal,
) -> None:
    await bet_repository.save(Bet.create(event_id=event_id, amount=amount))
    await bet_repository.save(Bet.create(event_id=event_id, amount=Decimal("25.00")))

    use_case = ListBetsUseCase(bet_repository)
    bets = await use_case.execute()

    assert len(bets) == 2


@pytest.mark.asyncio
async def test_finish_bet_use_case(
    bet_repository: PostgresBetRepository,
    event_id: str,
    amount: Decimal,
    now,
) -> None:
    bet = Bet.create(event_id=event_id, amount=amount)
    await bet_repository.save(bet)

    use_case = FinishBetUseCase(bet_repository)
    finished = await use_case.execute(bet.bet_id, FINISHED_WIN)

    assert finished.status == BetStatus.WON
    assert finished.finished_at is not None

    saved = await bet_repository.get_by_id(bet.bet_id)
    assert saved is not None
    assert saved.status == BetStatus.WON


@pytest.mark.asyncio
async def test_finish_bet_not_found(
    bet_repository: PostgresBetRepository,
) -> None:
    use_case = FinishBetUseCase(bet_repository)

    with pytest.raises(BetNotFoundError):
        await use_case.execute("missing-id", FINISHED_WIN)


@pytest.mark.asyncio
async def test_finish_bets_by_event_use_case(
    bet_repository: PostgresBetRepository,
    event_id: str,
    amount: Decimal,
) -> None:
    await bet_repository.save(Bet.create(event_id=event_id, amount=amount))
    await bet_repository.save(Bet.create(event_id=event_id, amount=Decimal("25.00")))
    await bet_repository.save(
        Bet.create(event_id="other-event", amount=Decimal("10.00"))
    )

    use_case = FinishBetsByEventUseCase(bet_repository)
    finished = await use_case.execute(event_id, FINISHED_LOSE)

    assert len(finished) == 2
    assert all(bet.status == BetStatus.LOST for bet in finished)

    other_event_pending = await bet_repository.list_pending_by_event_id("other-event")
    assert len(other_event_pending) == 1
