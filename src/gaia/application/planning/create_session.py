from gaia.application.ai.dto import CreateSessionRequest, ToolDefinitionDto
from gaia.application.planning.dtos import (
    PlanningSessionDto,
)
from gaia.application.planning.mappers import SessionMapper, ToolMapper
from gaia.application.planning.planning_service import PlanningService
from gaia.domain.planning.aggregates import PlanningSession
from gaia.domain.planning.repositories import PlanningSessionRepository


class CreateSessionUseCase:
    def __init__(self, repo: PlanningSessionRepository, llm: PlanningService):
        self._repo = repo
        self._llm = llm

    async def execute(self, request: CreateSessionRequest) -> PlanningSessionDto:
        tool_defs = [
            ToolMapper.to_domain(ToolDefinitionDto(**td))
            for td in request.tool_definitions
        ]
        session = PlanningSession.create(request.instruction, tool_defs)

        content, tool_calls, plan = await self._llm.think(session)
        session.add_ai_response(content, tool_calls, plan)

        await self._repo.save(session)
        return SessionMapper.to_dto(session)
