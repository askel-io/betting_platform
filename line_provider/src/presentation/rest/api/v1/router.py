from fastapi import APIRouter

from line_provider.src.presentation.rest.api.v1.events import router as events_router
from line_provider.src.presentation.rest.api.v1.health import router as health_router

router = APIRouter()
router.include_router(health_router)
router.include_router(events_router)
