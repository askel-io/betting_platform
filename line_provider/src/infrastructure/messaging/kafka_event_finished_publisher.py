import logging

from aiokafka import AIOKafkaProducer

from line_provider.src.application.dto.event_finished_message import EventFinishedMessage
from line_provider.src.application.ports.event_finished_publisher import EventFinishedPublisher

logger = logging.getLogger(__name__)


class KafkaEventFinishedPublisher(EventFinishedPublisher):
    def __init__(self, bootstrap_servers: str, topic: str) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers)
        await self._producer.start()
        logger.info("Kafka producer started for topic %s", self._topic)

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None
            logger.info("Kafka producer stopped")

    async def publish(self, event_id: str, state: str) -> None:
        if self._producer is None:
            raise RuntimeError("Kafka producer is not started")

        message = EventFinishedMessage(event_id=event_id, state=state)
        await self._producer.send_and_wait(self._topic, message.to_json())
