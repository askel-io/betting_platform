import pytest
from httpx import AsyncClient

from tests.scenarios.conftest import (
    create_event,
    finish_event,
    place_bet,
    wait_for_bet_status,
)

pytestmark = pytest.mark.scenario


@pytest.mark.asyncio
async def test_scenario_full_flow_blocks_bets_after_event_is_finished(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, bet_maker = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    first_bet = await place_bet(bet_maker, event_id=event_id, amount="50.00")
    assert first_bet.status_code == 201

    finish_response = await finish_event(line_provider, event_id, "finished_win")
    assert finish_response.status_code == 200

    await wait_for_bet_status(bet_maker, first_bet.json()["bet_id"], "won")

    second_bet = await place_bet(bet_maker, event_id=event_id, amount="25.00")
    assert second_bet.status_code == 409


@pytest.mark.asyncio
async def test_scenario_multiple_bets_finished_via_kafka_on_event_win(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, bet_maker = platform_clients
    created = await create_event(line_provider, coefficient="1.90")
    event_id = created["event_id"]

    bet_one = await place_bet(bet_maker, event_id=event_id, amount="10.00")
    bet_two = await place_bet(bet_maker, event_id=event_id, amount="20.00")
    bet_three = await place_bet(bet_maker, event_id=event_id, amount="30.00")
    assert bet_one.status_code == 201
    assert bet_two.status_code == 201
    assert bet_three.status_code == 201

    finish_response = await finish_event(line_provider, event_id, "finished_win")
    assert finish_response.status_code == 200

    for response in (bet_one, bet_two, bet_three):
        finished_bet = await wait_for_bet_status(
            bet_maker, response.json()["bet_id"], "won"
        )
        assert finished_bet["finished_at"] is not None


@pytest.mark.asyncio
async def test_scenario_multiple_bets_finished_via_kafka_on_event_lose(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, bet_maker = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    bet_one = await place_bet(bet_maker, event_id=event_id, amount="15.00")
    bet_two = await place_bet(bet_maker, event_id=event_id, amount="25.00")
    assert bet_one.status_code == 201
    assert bet_two.status_code == 201

    finish_response = await finish_event(line_provider, event_id, "finished_lose")
    assert finish_response.status_code == 200

    await wait_for_bet_status(bet_maker, bet_one.json()["bet_id"], "lost")
    await wait_for_bet_status(bet_maker, bet_two.json()["bet_id"], "lost")


@pytest.mark.asyncio
async def test_scenario_update_event_then_place_bet_succeeds(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, bet_maker = platform_clients
    created = await create_event(line_provider, coefficient="1.50")
    event_id = created["event_id"]

    update_response = await line_provider.patch(
        f"/rest/api/v1/events/{event_id}",
        json={"coefficient": "2.75"},
    )
    assert update_response.status_code == 200

    bet_response = await place_bet(bet_maker, event_id=event_id)
    assert bet_response.status_code == 201


@pytest.mark.asyncio
async def test_scenario_happy_path_kafka_auto_finishes_bet_as_won(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, bet_maker = platform_clients
    created = await create_event(line_provider, coefficient="1.85")
    event_id = created["event_id"]

    place_response = await place_bet(bet_maker, event_id=event_id, amount="100.00")
    bet_id = place_response.json()["bet_id"]

    finish_response = await finish_event(line_provider, event_id, "finished_win")
    assert finish_response.status_code == 200

    finished_bet = await wait_for_bet_status(bet_maker, bet_id, "won")

    assert finished_bet["status"] == "won"
    assert finished_bet["finished_at"] is not None

    event_response = await line_provider.get(f"/rest/api/v1/events/{event_id}")
    assert event_response.json()["state"] == "finished_win"


@pytest.mark.asyncio
async def test_scenario_happy_path_kafka_auto_finishes_bet_as_lost(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, bet_maker = platform_clients
    created = await create_event(line_provider, coefficient="2.10")
    event_id = created["event_id"]

    place_response = await place_bet(bet_maker, event_id=event_id, amount="55.00")
    bet_id = place_response.json()["bet_id"]

    finish_response = await finish_event(line_provider, event_id, "finished_lose")
    assert finish_response.status_code == 200

    finished_bet = await wait_for_bet_status(bet_maker, bet_id, "lost")

    assert finished_bet["status"] == "lost"
    assert finished_bet["finished_at"] is not None
