from fastapi import APIRouter
from gaia.presentation.api.routers import plan

def create_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(plan.router)
    return router
