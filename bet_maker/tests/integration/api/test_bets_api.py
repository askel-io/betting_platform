from collections.abc import AsyncGenerator
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from bet_maker.main import app
from bet_maker.src.application.dto.line_provider_event import LineProviderEventDTO
from bet_maker.src.domain.entities.bet import Bet, BetStatus, FINISHED_WIN
from bet_maker.src.infrastructure.db.session import get_session
from bet_maker.src.infrastructure.repositories.postgres_bet_repository import (
    PostgresBetRepository,
)
from bet_maker.src.presentation.rest.dependencies import get_line_provider
from bet_maker.tests.conftest import FakeLineProviderPort


@pytest.fixture
async def client(
    db_session: AsyncSession,
    fake_line_provider: FakeLineProviderPort,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    def override_line_provider() -> FakeLineProviderPort:
        return fake_line_provider

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_line_provider] = override_line_provider

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/rest/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "bet-maker"}


@pytest.mark.asyncio
async def test_place_bet(
    client: AsyncClient,
    event_id: str,
    amount: Decimal,
) -> None:
    response = await client.post(
        "/rest/api/v1/bet",
        json={"event_id": event_id, "amount": str(amount)},
    )

    assert response.status_code == 201
    assert "bet_id" in response.json()


@pytest.mark.asyncio
async def test_place_bet_event_not_found(
    client: AsyncClient,
    amount: Decimal,
) -> None:
    response = await client.post(
        "/rest/api/v1/bet",
        json={"event_id": "missing-event", "amount": str(amount)},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found: missing-event"


@pytest.mark.asyncio
async def test_place_bet_event_not_available(
    client: AsyncClient,
    fake_line_provider: FakeLineProviderPort,
    available_event: LineProviderEventDTO,
    amount: Decimal,
) -> None:
    finished_event = available_event.model_copy(update={"state": "finished_lose"})
    fake_line_provider.add_event(finished_event)

    response = await client.post(
        "/rest/api/v1/bet",
        json={"event_id": finished_event.event_id, "amount": str(amount)},
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == f"Event is not available for betting: {finished_event.event_id}"
    )


@pytest.mark.asyncio
async def test_get_bet(
    client: AsyncClient,
    bet_repository: PostgresBetRepository,
    event_id: str,
    amount: Decimal,
) -> None:
    bet = Bet.create(event_id=event_id, amount=amount)
    await bet_repository.save(bet)

    response = await client.get(f"/rest/api/v1/bets/{bet.bet_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["bet_id"] == bet.bet_id
    assert data["event_id"] == event_id
    assert data["amount"] == str(amount)
    assert data["status"] == BetStatus.PENDING.value


@pytest.mark.asyncio
async def test_get_bet_not_found(client: AsyncClient) -> None:
    response = await client.get("/rest/api/v1/bets/missing-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Bet not found: missing-id"


@pytest.mark.asyncio
async def test_list_bets(
    client: AsyncClient,
    bet_repository: PostgresBetRepository,
    event_id: str,
    amount: Decimal,
) -> None:
    await bet_repository.save(Bet.create(event_id=event_id, amount=amount))

    response = await client.get("/rest/api/v1/bets")

    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_finish_bet(
    client: AsyncClient,
    bet_repository: PostgresBetRepository,
    event_id: str,
    amount: Decimal,
) -> None:
    bet = Bet.create(event_id=event_id, amount=amount)
    await bet_repository.save(bet)

    response = await client.patch(
        f"/rest/api/v1/bets/{bet.bet_id}/finish",
        json={"state": FINISHED_WIN},
    )

    assert response.status_code == 200
    assert response.json()["status"] == BetStatus.WON.value
