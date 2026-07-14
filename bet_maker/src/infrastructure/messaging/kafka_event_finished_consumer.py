import asyncio
import logging

from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bet_maker.src.application.dto.event_finished_message import EventFinishedMessage
from bet_maker.src.application.use_cases.finish_bets_by_event import FinishBetsByEventUseCase
from bet_maker.src.infrastructure.repositories.postgres_bet_repository import (
    PostgresBetRepository,
)

logger = logging.getLogger(__name__)


class KafkaEventFinishedConsumer:
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._group_id = group_id
        self._session_factory = session_factory
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            auto_offset_reset="earliest",
        )
        await self._consumer.start()
        self._task = asyncio.create_task(self._consume())
        logger.info(
            "Kafka consumer started for topic %s (group %s)",
            self._topic,
            self._group_id,
        )

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None
            logger.info("Kafka consumer stopped")

    async def _consume(self) -> None:
        if self._consumer is None:
            return

        async for message in self._consumer:
            try:
                payload = message.value
                if not isinstance(payload, bytes):
                    logger.warning(
                        "Skipping Kafka message with invalid payload type: %s",
                        type(payload).__name__,
                    )
                    continue
                await self._handle_message(payload)
            except Exception:
                logger.exception("Failed to process Kafka message")

    async def _handle_message(self, payload: bytes) -> None:
        event_message = EventFinishedMessage.from_json(payload)

        async with self._session_factory() as session:
            repository = PostgresBetRepository(session)
            use_case = FinishBetsByEventUseCase(repository)
            finished_bets = await use_case.execute(
                event_id=event_message.event_id,
                event_state=event_message.state,
            )

        logger.info(
            "Finished %s bets for event %s with state %s",
            len(finished_bets),
            event_message.event_id,
            event_message.state,
        )
