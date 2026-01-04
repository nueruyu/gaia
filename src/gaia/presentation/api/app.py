from fastapi import FastAPI
from gaia.presentation.api.routers import plan


def create_app() -> FastAPI:
    app = FastAPI(
        title="Game AI Agent Server (Clean Architecture)",
        description="An API server to generate strategic plans for game AI agents using LangGraph.",
        version="1.1.0",
    )
    app.include_router(plan.router)
    return app
