import os

os.environ.setdefault("KAFKA_ENABLED", "false")

from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from line_provider.src.infrastructure.db.base import Base
from line_provider.src.infrastructure.db.models import EventModel  # noqa: F401
from line_provider.src.infrastructure.repositories.postgres_event_repository import (
    PostgresEventRepository,
)
from config.settings import get_settings

TEST_DATABASE_URL = get_settings().line_provider_database_url


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
        await connection.execute(text("TRUNCATE TABLE events"))

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    session = session_factory()

    try:
        yield session
    finally:
        await session.close()
        async with engine.begin() as connection:
            await connection.execute(text("TRUNCATE TABLE events"))


@pytest_asyncio.fixture
async def event_repository(db_session: AsyncSession) -> PostgresEventRepository:
    return PostgresEventRepository(db_session)


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def future_deadline(now: datetime) -> datetime:
    return datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)


@pytest.fixture
def coefficient() -> Decimal:
    return Decimal("2.50")
