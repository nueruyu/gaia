from gaia.application.ai.dto import (
    SubmitToolOutputsRequest,
    ToolDefinitionDto,
    ToolOutputDto,
)
from gaia.application.ai.mapper import AIMapper
from gaia.application.planning.dtos import PlanningSessionDto
from gaia.application.planning.mapper import PlanningMapper
from gaia.application.planning.planning_session_service import PlanningSessionService
from gaia.domain.planning.planning_session_repository import PlanningSessionRepository


class SubmitToolOutputsUseCase:
    def __init__(
        self,
        session_repository: PlanningSessionRepository,
        planning_session_service: PlanningSessionService,
    ):
        self._session_repository = session_repository
        self._planning_session_service = planning_session_service

    async def execute(
        self, session_id: str, request: SubmitToolOutputsRequest
    ) -> PlanningSessionDto:
        session = await self._session_repository.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        outputs = [
            AIMapper.to_tool_output(ToolOutputDto(**o)) for o in request.tool_outputs
        ]
        tool_defs = [
            AIMapper.to_tool_definition(ToolDefinitionDto(**td))
            for td in request.tool_definitions
        ]

        session.add_tool_outputs(outputs, tool_defs)

        await self._planning_session_service.advance(session)

        return PlanningMapper.to_planning_session_dto(session)
