from contextlib import asynccontextmanager

from fastapi import FastAPI

from bet_maker.src.infrastructure.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_CONSUMER_GROUP,
    KAFKA_ENABLED,
    KAFKA_EVENT_FINISHED_TOPIC,
)
from bet_maker.src.infrastructure.db.session import SessionLocal
from bet_maker.src.infrastructure.messaging.kafka_event_finished_consumer import (
    KafkaEventFinishedConsumer,
)
from bet_maker.src.presentation.rest.api.v1.router import router as v1_router
from bet_maker.src.presentation.rest.dependencies import close_http_client
from bet_maker.src.presentation.rest.exception_handlers import (
    register_exception_handlers,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if KAFKA_ENABLED:
        consumer = KafkaEventFinishedConsumer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            topic=KAFKA_EVENT_FINISHED_TOPIC,
            group_id=KAFKA_CONSUMER_GROUP,
            session_factory=SessionLocal,
        )
        await consumer.start()
        try:
            yield
        finally:
            await consumer.stop()
            await close_http_client()
    else:
        try:
            yield
        finally:
            await close_http_client()


app = FastAPI(title="Bet Maker", version="0.1.0", lifespan=lifespan)
app.include_router(v1_router, prefix="/rest/api/v1")
register_exception_handlers(app)
