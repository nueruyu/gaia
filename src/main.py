import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI

from gaia.containers import Container
from gaia.presentation.api.app import create_api_router
from gaia.presentation.api.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = app.state.container
    repo = container.planning_repo()
    await repo.initialize()
    yield


def create_app():
    load_dotenv()
    container = Container()
    container.wire(modules=["gaia.presentation.api.routers.plan"])

    app = FastAPI(title="Gaia AI Server", version="2.0.0", lifespan=lifespan)
    app.state.container = container

    register_exception_handlers(app)

    api_router = create_api_router()
    app.include_router(api_router)

    return app


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
