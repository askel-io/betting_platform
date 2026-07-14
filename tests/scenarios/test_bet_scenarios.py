import pytest
from httpx import AsyncClient

from tests.scenarios.conftest import create_event, finish_event, place_bet

pytestmark = pytest.mark.scenario


@pytest.mark.asyncio
async def test_scenario_place_bet_when_event_exists(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, bet_maker = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    response = await place_bet(bet_maker, event_id=event_id, amount="100.00")

    assert response.status_code == 201
    assert "bet_id" in response.json()


@pytest.mark.asyncio
async def test_scenario_reject_bet_on_unknown_event(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    _, bet_maker = platform_clients

    response = await place_bet(bet_maker, event_id="unknown-event-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found: unknown-event-id"


@pytest.mark.asyncio
async def test_scenario_reject_bet_on_finished_event(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, bet_maker = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    finish_response = await finish_event(line_provider, event_id, "finished_win")
    assert finish_response.status_code == 200

    response = await place_bet(bet_maker, event_id=event_id)

    assert response.status_code == 409
    assert (
        response.json()["detail"] == f"Event is not available for betting: {event_id}"
    )


@pytest.mark.asyncio
async def test_scenario_reject_bet_with_invalid_amount(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, bet_maker = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    response = await place_bet(bet_maker, event_id=event_id, amount="0.00")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_scenario_get_and_list_bets(
    platform_clients: tuple[AsyncClient, AsyncClient]
):
    line_provider, bet_maker = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    place_response = await place_bet(bet_maker, event_id=event_id, amount="75.00")
    bet_id = place_response.json()["bet_id"]

    get_response = await bet_maker.get(f"/rest/api/v1/bets/{bet_id}")
    assert get_response.status_code == 200
    assert get_response.json()["event_id"] == event_id
    assert get_response.json()["amount"] == "75.00"
    assert get_response.json()["status"] == "pending"

    list_response = await bet_maker.get("/rest/api/v1/bets")
    assert list_response.status_code == 200
    assert any(bet["bet_id"] == bet_id for bet in list_response.json())


@pytest.mark.asyncio
async def test_scenario_manual_finish_bet_as_won(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, bet_maker = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    place_response = await place_bet(bet_maker, event_id=event_id)
    bet_id = place_response.json()["bet_id"]

    finish_response = await bet_maker.patch(
        f"/rest/api/v1/bets/{bet_id}/finish",
        json={"state": "finished_win"},
    )

    assert finish_response.status_code == 200
    assert finish_response.json()["status"] == "won"
    assert finish_response.json()["finished_at"] is not None


@pytest.mark.asyncio
async def test_scenario_manual_finish_bet_as_lost(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, bet_maker = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    place_response = await place_bet(bet_maker, event_id=event_id)
    bet_id = place_response.json()["bet_id"]

    finish_response = await bet_maker.patch(
        f"/rest/api/v1/bets/{bet_id}/finish",
        json={"state": "finished_lose"},
    )

    assert finish_response.status_code == 200
    assert finish_response.json()["status"] == "lost"


@pytest.mark.asyncio
async def test_scenario_get_missing_bet_returns_404(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    _, bet_maker = platform_clients

    response = await bet_maker.get("/rest/api/v1/bets/missing-bet-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Bet not found: missing-bet-id"
