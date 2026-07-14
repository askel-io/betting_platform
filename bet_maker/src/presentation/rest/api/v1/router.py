from fastapi import APIRouter

from bet_maker.src.presentation.rest.api.v1.health import router as health_router

router = APIRouter()
router.include_router(health_router)
