import logging
import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from gaia.containers import Container
from gaia.presentation.api.app import create_api_router
from gaia.presentation.api.exception_handlers import register_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        client_host = request.client.host if request.client else "unknown"
        logger.info(
            f"Request: {request.method} {request.url.path} - Client: {client_host}"
        )
        response = await call_next(request)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = app.state.container

    # Manual initialization logic (unchanged)
    repo = container.planning_repo()
    await repo.initialize()

    yield

    # Generic shutdown logic
    lifecycle = container.lifecycle_manager()
    await lifecycle.shutdown()


def create_app():
    load_dotenv()
    container = Container()
    container.wire(modules=["gaia.presentation.api.routers.plan"])

    app = FastAPI(title="Gaia AI Server", version="2.0.0", lifespan=lifespan)
    app.state.container = container

    app.add_middleware(RequestLoggingMiddleware)
    register_exception_handlers(app)

    api_router = create_api_router()
    app.include_router(api_router)

    return app


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
