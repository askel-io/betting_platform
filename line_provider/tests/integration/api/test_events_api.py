from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from line_provider.main import app
from line_provider.src.domain.entities.event import Event, EventState
from line_provider.src.infrastructure.db.session import get_session
from line_provider.src.infrastructure.repositories.postgres_event_repository import (
    PostgresEventRepository,
)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/rest/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "line-provider"}


@pytest.mark.asyncio
async def test_create_event(client: AsyncClient) -> None:
    response = await client.post(
        "/rest/api/v1/events",
        json={
            "coefficient": "2.50",
            "deadline": "2026-07-15T18:00:00Z",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["coefficient"] == "2.50"
    assert data["state"] == EventState.NEW.value
    assert "eventId" in data


@pytest.mark.asyncio
async def test_get_event(
    client: AsyncClient,
    event_repository: PostgresEventRepository,
    coefficient,
    future_deadline,
    now,
) -> None:
    event = Event.create(coefficient, future_deadline, now=now)
    await event_repository.save(event)

    response = await client.get(f"/rest/api/v1/events/{event.eventId}")

    assert response.status_code == 200
    assert response.json()["eventId"] == event.eventId


@pytest.mark.asyncio
async def test_get_event_not_found(client: AsyncClient) -> None:
    response = await client.get("/rest/api/v1/events/missing-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_events(
    client: AsyncClient,
    event_repository: PostgresEventRepository,
    coefficient,
    future_deadline,
    now,
) -> None:
    event = Event.create(coefficient, future_deadline, now=now)
    await event_repository.save(event)

    response = await client.get("/rest/api/v1/events")

    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_update_event(
    client: AsyncClient,
    event_repository: PostgresEventRepository,
    coefficient,
    future_deadline,
    now,
) -> None:
    event = Event.create(coefficient, future_deadline, now=now)
    await event_repository.save(event)

    response = await client.patch(
        f"/rest/api/v1/events/{event.eventId}",
        json={"coefficient": "4.00"},
    )

    assert response.status_code == 200
    assert response.json()["coefficient"] == "4.00"


@pytest.mark.asyncio
async def test_update_finished_event_returns_409(
    client: AsyncClient,
    event_repository: PostgresEventRepository,
    coefficient,
    future_deadline,
    now,
) -> None:
    event = Event.create(coefficient, future_deadline, now=now)
    event.finish_win()
    await event_repository.save(event)

    response = await client.patch(
        f"/rest/api/v1/events/{event.eventId}",
        json={"coefficient": "4.00"},
    )

    assert response.status_code == 409
