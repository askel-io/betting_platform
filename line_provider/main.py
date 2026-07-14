from contextlib import asynccontextmanager

from fastapi import FastAPI

from line_provider.src.infrastructure.config import KAFKA_ENABLED
from line_provider.src.infrastructure.messaging.noop_event_finished_publisher import (
    NoOpEventFinishedPublisher,
)
from line_provider.src.infrastructure.messaging.publisher_registry import (
    create_event_finished_publisher,
    set_event_finished_publisher,
)
from line_provider.src.presentation.rest.api.v1.router import router as v1_router
from line_provider.src.presentation.rest.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if KAFKA_ENABLED:
        publisher = create_event_finished_publisher()
        await publisher.start()
        set_event_finished_publisher(publisher)
        yield
        await publisher.stop()
    else:
        set_event_finished_publisher(NoOpEventFinishedPublisher())
        yield


app = FastAPI(title="Line Provider", version="0.1.0", lifespan=lifespan)
app.include_router(v1_router, prefix="/rest/api/v1")
register_exception_handlers(app)
