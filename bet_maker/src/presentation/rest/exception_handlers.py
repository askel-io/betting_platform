from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from bet_maker.src.errors.bet_error import BetNotFoundError, InvalidAmountError
from bet_maker.src.errors.domain_error import DomainError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidAmountError)
    async def invalid_amount_handler(
        _request: Request,
        exc: InvalidAmountError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": f"Invalid amount: {exc.args[0]}"},
        )

    @app.exception_handler(BetNotFoundError)
    async def bet_not_found_handler(
        _request: Request,
        exc: BetNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Bet not found: {exc.bet_id}"},
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(
        _request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
