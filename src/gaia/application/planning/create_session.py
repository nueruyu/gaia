from gaia.application.ai.dto import CreateSessionRequest, ToolDefinitionDto
from gaia.application.planning.dtos import (
    PlanningSessionDto,
)
from gaia.application.planning.mappers import SessionMapper, ToolMapper
from gaia.application.planning.planning_service import PlanningService
from gaia.domain.planning.aggregates import PlanningSession
from gaia.domain.planning.repositories import PlanningSessionRepository


class CreateSessionUseCase:
    def __init__(
        self,
        session_repository: PlanningSessionRepository,
        planning_service: PlanningService,
    ):
        self._session_repository = session_repository
        self._planning_service = planning_service

    async def execute(self, request: CreateSessionRequest) -> PlanningSessionDto:
        tool_defs = [
            ToolMapper.to_domain(ToolDefinitionDto(**td))
            for td in request.tool_definitions
        ]
        session = PlanningSession.create(request.instruction, tool_defs)

        content, tool_calls, plan = await self._planning_service.think(session)
        session.add_ai_response(content, tool_calls, plan)

        await self._session_repository.save(session)
        return SessionMapper.to_dto(session)
