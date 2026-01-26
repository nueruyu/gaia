from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from gaia.application.ai.dto import SubmitToolOutputsRequest
from gaia.application.planning.create_session_use_case import CreateSessionUseCase
from gaia.application.planning.dtos import (
    CreateSessionRequest,
    PlanningSessionDto,
)
from gaia.application.planning.submit_tool_outputs_use_case import (
    SubmitToolOutputsUseCase,
)
from gaia.containers import Container

router = APIRouter(prefix="/planning", tags=["Planning"])


@router.post("/request", response_model=PlanningSessionDto)
@inject
async def create_session(
    request: CreateSessionRequest,
    use_case: CreateSessionUseCase = Depends(
        Provide[Container.create_session_use_case]
    ),
):
    try:
        return await use_case.execute(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/respond/{session_id}", response_model=PlanningSessionDto)
@inject
async def submit_tool_outputs(
    session_id: str,
    request: SubmitToolOutputsRequest,
    use_case: SubmitToolOutputsUseCase = Depends(
        Provide[Container.submit_tool_outputs_use_case]
    ),
):
    try:
        return await use_case.execute(session_id, request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
