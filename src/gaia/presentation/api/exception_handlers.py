import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from gaia.domain.core.exceptions import DomainError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(DomainError, handle_domain_error)
    app.add_exception_handler(ValueError, handle_value_error)
    app.add_exception_handler(Exception, handle_generic_exception)


async def handle_domain_error(request: Request, exc: Exception):
    logger.warning("Domain error occurred: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


async def handle_value_error(request: Request, exc: Exception):
    logger.warning("Value error occurred: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


async def handle_generic_exception(request: Request, exc: Exception):
    logger.error("An unhandled exception occurred: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )
