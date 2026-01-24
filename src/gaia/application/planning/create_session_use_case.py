from gaia.application.ai.dto import CreateSessionRequest, ToolDefinitionDto
from gaia.application.ai.mapper import AIMapper
from gaia.application.planning.dtos import PlanningSessionDto
from gaia.application.planning.mapper import PlanningMapper
from gaia.application.planning.planning_session_service import PlanningSessionService
from gaia.domain.planning.planning_session import PlanningSession


class CreateSessionUseCase:
    def __init__(self, planning_session_service: PlanningSessionService):
        self._planning_session_service = planning_session_service

    async def execute(self, request: CreateSessionRequest) -> PlanningSessionDto:
        tool_defs = [
            AIMapper.to_tool_definition(ToolDefinitionDto(**td))
            for td in request.tool_definitions
        ]
        session = PlanningSession.create(request.instruction, tool_defs)

        await self._planning_session_service.advance(session)

        return PlanningMapper.to_planning_session_dto(session)
