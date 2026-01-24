import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from gaia.containers import Container
from gaia.presentation.api.app import create_api_router


def create_app():
    # Load environment variables from .env file
    load_dotenv()

    # Create the DI container instance
    container = Container()

    # Wire the container to the modules that need injection.
    container.wire(modules=["gaia.presentation.api.routers.plan"])

    # Create the FastAPI app instance and include routers
    app = FastAPI(
        title="Game AI Agent Server (Reloadable)",
        description="An API server using a clean, reloadable architecture.",
        version="1.2.0",
    )

    # Get the router from the presentation layer
    api_router = create_api_router()
    app.include_router(api_router)

    return app


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
