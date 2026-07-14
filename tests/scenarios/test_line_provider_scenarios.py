import pytest
from httpx import AsyncClient

from tests.scenarios.conftest import (
    FUTURE_DEADLINE,
    PAST_DEADLINE,
    create_event,
    finish_event,
)

pytestmark = pytest.mark.scenario


@pytest.mark.asyncio
async def test_scenario_create_event_and_retrieve_it(
    platform_clients: tuple[AsyncClient, AsyncClient]
):
    line_provider, _ = platform_clients

    created = await create_event(line_provider)
    event_id = created["event_id"]

    response = await line_provider.get(f"/rest/api/v1/events/{event_id}")

    assert response.status_code == 200
    assert response.json()["event_id"] == event_id
    assert response.json()["state"] == "new"
    assert response.json()["coefficient"] == "2.50"


@pytest.mark.asyncio
async def test_scenario_list_events_includes_created_event(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, _ = platform_clients

    created = await create_event(line_provider, coefficient="3.25")

    response = await line_provider.get("/rest/api/v1/events")

    assert response.status_code == 200
    event_ids = {event["event_id"] for event in response.json()}
    assert created["event_id"] in event_ids


@pytest.mark.asyncio
async def test_scenario_update_coefficient_on_open_event(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, _ = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    response = await line_provider.patch(
        f"/rest/api/v1/events/{event_id}",
        json={"coefficient": "4.00"},
    )

    assert response.status_code == 200
    assert response.json()["coefficient"] == "4.00"


@pytest.mark.asyncio
async def test_scenario_update_deadline_on_open_event(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, _ = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]
    new_deadline = "2027-01-15T12:00:00Z"

    response = await line_provider.patch(
        f"/rest/api/v1/events/{event_id}",
        json={"deadline": new_deadline},
    )

    assert response.status_code == 200
    assert response.json()["deadline"] == new_deadline


@pytest.mark.asyncio
async def test_scenario_reject_update_on_finished_event(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, _ = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    finish_response = await finish_event(line_provider, event_id, "finished_win")
    assert finish_response.status_code == 200

    response = await line_provider.patch(
        f"/rest/api/v1/events/{event_id}",
        json={"coefficient": "5.00"},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_scenario_finish_event_as_win(
    platform_clients: tuple[AsyncClient, AsyncClient]
):
    line_provider, _ = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    response = await finish_event(line_provider, event_id, "finished_win")

    assert response.status_code == 200
    assert response.json()["state"] == "finished_win"


@pytest.mark.asyncio
async def test_scenario_finish_event_as_lose(
    platform_clients: tuple[AsyncClient, AsyncClient]
):
    line_provider, _ = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    response = await finish_event(line_provider, event_id, "finished_lose")

    assert response.status_code == 200
    assert response.json()["state"] == "finished_lose"


@pytest.mark.asyncio
async def test_scenario_reject_double_finish(
    platform_clients: tuple[AsyncClient, AsyncClient]
):
    line_provider, _ = platform_clients
    created = await create_event(line_provider)
    event_id = created["event_id"]

    first_finish = await finish_event(line_provider, event_id, "finished_win")
    assert first_finish.status_code == 200

    second_finish = await finish_event(line_provider, event_id, "finished_lose")

    assert second_finish.status_code == 409


@pytest.mark.asyncio
async def test_scenario_get_missing_event_returns_404(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, _ = platform_clients

    response = await line_provider.get("/rest/api/v1/events/missing-event-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_scenario_reject_create_event_with_past_deadline(
    platform_clients: tuple[AsyncClient, AsyncClient],
):
    line_provider, _ = platform_clients

    response = await line_provider.post(
        "/rest/api/v1/events",
        json={"coefficient": "2.50", "deadline": PAST_DEADLINE},
    )

    assert response.status_code == 400
