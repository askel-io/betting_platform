from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from line_provider.src.errors.domain_error import DomainError
from line_provider.src.errors.event_error import (
    EventAlreadyFinishedError,
    EventNotEditableError,
    EventNotFoundError,
    InvalidCoefficientError,
    InvalidDeadlineError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidCoefficientError)
    async def invalid_coefficient_handler(
        _request: Request,
        exc: InvalidCoefficientError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": f"Invalid coefficient: {exc.args[0]}"},
        )

    @app.exception_handler(InvalidDeadlineError)
    async def invalid_deadline_handler(
        _request: Request,
        exc: InvalidDeadlineError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc.args[0]) if exc.args else "Invalid deadline"},
        )

    @app.exception_handler(EventNotFoundError)
    async def event_not_found_handler(
        _request: Request,
        exc: EventNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Event not found: {exc.event_id}"},
        )

    @app.exception_handler(EventAlreadyFinishedError)
    async def event_already_finished_handler(
        _request: Request,
        exc: EventAlreadyFinishedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": f"Event already finished: {exc.args[0]}"},
        )

    @app.exception_handler(EventNotEditableError)
    async def event_not_editable_handler(
        _request: Request,
        exc: EventNotEditableError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": f"Event is not editable: {exc.event_id}"},
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
