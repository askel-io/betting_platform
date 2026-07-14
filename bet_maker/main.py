from fastapi import FastAPI

from bet_maker.src.presentation.rest.api.v1.router import router as v1_router
from bet_maker.src.presentation.rest.exception_handlers import register_exception_handlers

app = FastAPI(title="Bet Maker", version="0.1.0")
app.include_router(v1_router, prefix="/rest/api/v1")
register_exception_handlers(app)
