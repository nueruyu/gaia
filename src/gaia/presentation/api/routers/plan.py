from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from gaia.application.use_cases.create_session import CreateSessionUseCase
from gaia.application.use_cases.submit_tool_outputs import SubmitToolOutputsUseCase
from gaia.containers import Container
from gaia.presentation.api.schemas import (
    CreateSessionRequest,
    SubmitToolOutputsRequest,
    SessionResponse,
)
from gaia.application.dtos import ToolDefinitionDto, ToolOutputDto

router = APIRouter(prefix="/planning", tags=["Planning"])


@router.post("/request", response_model=SessionResponse)
@inject
async def create_session(
    request: CreateSessionRequest,
    use_case: CreateSessionUseCase = Depends(
        Provide[Container.create_session_use_case]
    ),
):
    try:
        tool_defs = [ToolDefinitionDto(**td) for td in request.tool_definitions]
        return await use_case.execute(request.instruction, tool_defs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/respond/{session_id}", response_model=SessionResponse)
@inject
async def submit_tool_outputs(
    session_id: str,
    request: SubmitToolOutputsRequest,
    use_case: SubmitToolOutputsUseCase = Depends(
        Provide[Container.submit_tool_outputs_use_case]
    ),
):
    try:
        outputs = [ToolOutputDto(**o) for o in request.tool_outputs]
        tool_defs = [ToolDefinitionDto(**td) for td in request.tool_definitions]
        return await use_case.execute(session_id, outputs, tool_defs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
