import os

os.environ.setdefault("KAFKA_ENABLED", "false")

from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from bet_maker.src.application.dto.line_provider_event import LineProviderEventDTO
from bet_maker.src.application.ports.line_provider_port import LineProviderPort
from bet_maker.src.infrastructure.db.base import Base
from bet_maker.src.infrastructure.db.models.bet_model import BetModel  # noqa: F401
from bet_maker.src.infrastructure.repositories.postgres_bet_repository import (
    PostgresBetRepository,
)

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://bet_maker:bet_maker@localhost:5434/bet_maker",
)


class FakeLineProviderPort(LineProviderPort):
    def __init__(self, events: dict[str, LineProviderEventDTO] | None = None) -> None:
        self._events = events or {}

    async def get_event(self, event_id: str) -> LineProviderEventDTO | None:
        return self._events.get(event_id)

    def add_event(self, event: LineProviderEventDTO) -> None:
        self._events[event.event_id] = event


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield test_engine

    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE bets"))

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    session = session_factory()

    try:
        yield session
    finally:
        await session.close()
        async with engine.begin() as connection:
            await connection.execute(text("TRUNCATE TABLE bets"))


@pytest_asyncio.fixture
async def bet_repository(db_session: AsyncSession) -> PostgresBetRepository:
    return PostgresBetRepository(db_session)


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def future_deadline(now: datetime) -> datetime:
    return datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)


@pytest.fixture
def past_deadline(now: datetime) -> datetime:
    return datetime(2026, 7, 13, 18, 0, tzinfo=timezone.utc)


@pytest.fixture
def event_id() -> str:
    return "event-123"


@pytest.fixture
def amount() -> Decimal:
    return Decimal("100.00")


@pytest.fixture
def available_event(
    event_id: str,
    future_deadline: datetime,
    now: datetime,
) -> LineProviderEventDTO:
    return LineProviderEventDTO(
        event_id=event_id,
        coefficient=Decimal("2.50"),
        deadline=future_deadline,
        state="new",
        created_at=now,
    )


@pytest.fixture
def fake_line_provider(available_event: LineProviderEventDTO) -> FakeLineProviderPort:
    provider = FakeLineProviderPort()
    provider.add_event(available_event)
    return provider
