from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from gaia.application.use_cases.create_plan import CreatePlanUseCase
from gaia.containers import Container
from gaia.presentation.api.schemas import ApiPlanRequest, ApiPlanResponse

router = APIRouter()


@router.post(
    "/request_plan",
    response_model=ApiPlanResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["AI Planning"],
)
@inject
def request_plan_endpoint(
    request: ApiPlanRequest,
    create_plan_use_case: CreatePlanUseCase = Depends(
        Provide[Container.create_plan_use_case]
    ),
):
    """Receives game state and context, then returns a strategic plan for an AI agent."""
    try:
        plan = create_plan_use_case.execute(request)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/health", tags=["System"])
def health_check():
    """A simple health check endpoint."""
    return {"status": "ok"}
