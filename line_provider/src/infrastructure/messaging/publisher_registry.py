from line_provider.src.application.ports.event_finished_publisher import (
    EventFinishedPublisher,
)
from line_provider.src.infrastructure.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_EVENT_FINISHED_TOPIC,
)
from line_provider.src.infrastructure.messaging.kafka_event_finished_publisher import (
    KafkaEventFinishedPublisher,
)

_publisher: EventFinishedPublisher | None = None


def create_event_finished_publisher() -> KafkaEventFinishedPublisher:
    return KafkaEventFinishedPublisher(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        topic=KAFKA_EVENT_FINISHED_TOPIC,
    )


def set_event_finished_publisher(publisher: EventFinishedPublisher) -> None:
    global _publisher
    _publisher = publisher


def get_event_finished_publisher() -> EventFinishedPublisher:
    if _publisher is None:
        raise RuntimeError("Event finished publisher is not initialized")
    return _publisher
