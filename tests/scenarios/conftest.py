import os
import socket
import uuid

os.environ["KAFKA_ENABLED"] = "true"
os.environ.setdefault("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
os.environ.setdefault("KAFKA_EVENT_FINISHED_TOPIC", "event.finished")
os.environ["KAFKA_CONSUMER_GROUP"] = f"bet-maker-scenarios-{uuid.uuid4().hex[:8]}"

from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack
from datetime import datetime, timezone
from decimal import Decimal

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bet_maker.main import app as bet_maker_app
from bet_maker.main import lifespan as bet_maker_lifespan
from bet_maker.src.infrastructure.clients.line_provider_client import LineProviderClient
from bet_maker.src.infrastructure.db.base import Base as BetMakerBase
from bet_maker.src.infrastructure.db.models.bet_model import BetModel  # noqa: F401
from bet_maker.src.infrastructure.db.session import get_session as get_bet_maker_session
from bet_maker.src.presentation.rest.dependencies import get_line_provider
from line_provider.main import app as line_provider_app
from line_provider.main import lifespan as line_provider_lifespan
from line_provider.src.infrastructure.db.base import Base as LineProviderBase
from line_provider.src.infrastructure.db.models.event_model import (  # noqa: F401
    EventModel,
)
from line_provider.src.infrastructure.db.session import (
    get_session as get_line_provider_session,
)

LINE_PROVIDER_TEST_DATABASE_URL = os.getenv(
    "LINE_PROVIDER_TEST_DATABASE_URL",
    "postgresql+asyncpg://line_provider:line_provider@localhost:5433/line_provider_test",
)
BET_MAKER_TEST_DATABASE_URL = os.getenv(
    "BET_MAKER_TEST_DATABASE_URL",
    "postgresql+asyncpg://bet_maker:bet_maker@localhost:5434/bet_maker_test",
)

FUTURE_DEADLINE = "2026-12-31T23:59:59Z"
PAST_DEADLINE = "2020-01-01T00:00:00Z"


def kafka_is_available() -> bool:
    try:
        with socket.create_connection(
            (os.environ["KAFKA_BOOTSTRAP_SERVERS"].split(":")[0], 9092),
            timeout=2,
        ):
            return True
    except OSError:
        return False


@pytest.fixture(scope="session", autouse=True)
def require_kafka() -> None:
    if not kafka_is_available():
        pytest.skip(
            "Kafka is not available on localhost:9092. Run: docker compose up -d kafka"
        )


@pytest_asyncio.fixture
async def line_provider_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(LINE_PROVIDER_TEST_DATABASE_URL, echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(LineProviderBase.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def bet_maker_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(BET_MAKER_TEST_DATABASE_URL, echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(BetMakerBase.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def line_provider_db_session(
    line_provider_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    async with line_provider_engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE events"))

    session_factory = async_sessionmaker(line_provider_engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()
        async with line_provider_engine.begin() as connection:
            await connection.execute(text("TRUNCATE TABLE events"))


@pytest_asyncio.fixture
async def bet_maker_db_session(
    bet_maker_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    async with bet_maker_engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE bets"))

    session_factory = async_sessionmaker(bet_maker_engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()
        async with bet_maker_engine.begin() as connection:
            await connection.execute(text("TRUNCATE TABLE bets"))


@pytest_asyncio.fixture
async def platform_clients(
    line_provider_engine: AsyncEngine,
    bet_maker_engine: AsyncEngine,
    line_provider_db_session: AsyncSession,
    bet_maker_db_session: AsyncSession,
) -> AsyncGenerator[tuple[AsyncClient, AsyncClient], None]:
    async def override_line_provider_session() -> AsyncGenerator[AsyncSession, None]:
        yield line_provider_db_session

    async def override_bet_maker_session() -> AsyncGenerator[AsyncSession, None]:
        yield bet_maker_db_session

    line_provider_app.dependency_overrides[get_line_provider_session] = (
        override_line_provider_session
    )
    bet_maker_app.dependency_overrides[get_bet_maker_session] = (
        override_bet_maker_session
    )

    bet_maker_test_session_factory = async_sessionmaker(
        bet_maker_engine,
        expire_on_commit=False,
    )
    import bet_maker.main as bet_maker_main_module

    original_session_local = bet_maker_main_module.SessionLocal
    bet_maker_main_module.SessionLocal = bet_maker_test_session_factory

    line_provider_http: httpx.AsyncClient | None = None

    try:
        async with AsyncExitStack() as stack:
            await stack.enter_async_context(line_provider_lifespan(line_provider_app))
            await stack.enter_async_context(bet_maker_lifespan(bet_maker_app))

            line_provider_transport = ASGITransport(app=line_provider_app)
            line_provider_http = httpx.AsyncClient(
                transport=line_provider_transport,
                base_url="http://line-provider",
            )

            def override_line_provider() -> LineProviderClient:
                assert line_provider_http is not None
                return LineProviderClient("http://line-provider", line_provider_http)

            bet_maker_app.dependency_overrides[get_line_provider] = (
                override_line_provider
            )

            bet_maker_transport = ASGITransport(app=bet_maker_app)
            async with (
                AsyncClient(
                    transport=line_provider_transport,
                    base_url="http://line-provider",
                ) as line_provider_client,
                AsyncClient(
                    transport=bet_maker_transport,
                    base_url="http://bet-maker",
                ) as bet_maker_client,
            ):
                yield line_provider_client, bet_maker_client
    finally:
        bet_maker_main_module.SessionLocal = original_session_local
        bet_maker_app.dependency_overrides.clear()
        line_provider_app.dependency_overrides.clear()
        if line_provider_http is not None:
            await line_provider_http.aclose()


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def bet_amount() -> Decimal:
    return Decimal("100.00")


async def create_event(
    client: AsyncClient,
    *,
    coefficient: str = "2.50",
    deadline: str = FUTURE_DEADLINE,
) -> dict:
    response = await client.post(
        "/rest/api/v1/events",
        json={"coefficient": coefficient, "deadline": deadline},
    )
    assert response.status_code == 201
    return response.json()


async def place_bet(
    client: AsyncClient,
    *,
    event_id: str,
    amount: str = "100.00",
) -> httpx.Response:
    return await client.post(
        "/rest/api/v1/bet",
        json={"event_id": event_id, "amount": amount},
    )


async def finish_event(
    client: AsyncClient,
    event_id: str,
    state: str,
) -> httpx.Response:
    return await client.patch(
        f"/rest/api/v1/events/{event_id}/finish",
        json={"state": state},
    )


async def wait_for_bet_status(
    client: AsyncClient,
    bet_id: str,
    expected_status: str,
    *,
    attempts: int = 20,
    delay_seconds: float = 0.25,
) -> dict:
    import asyncio

    last_payload: dict = {}
    for _ in range(attempts):
        response = await client.get(f"/rest/api/v1/bets/{bet_id}")
        assert response.status_code == 200
        last_payload = response.json()
        if last_payload["status"] == expected_status:
            return last_payload
        await asyncio.sleep(delay_seconds)

    raise AssertionError(
        f"Bet {bet_id} did not reach status {expected_status}. "
        f"Last state: {last_payload}"
    )
