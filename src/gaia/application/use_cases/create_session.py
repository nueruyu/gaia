from typing import List
from gaia.application.interfaces.llm_service import LlmService
from gaia.domain.repositories import PlanningSessionRepository
from gaia.domain.aggregates import PlanningSession
from gaia.application.dtos import SessionDto, ToolDefinitionDto
from gaia.application.mappers import SessionMapper, ToolMapper

class CreateSessionUseCase:
    def __init__(self, repo: PlanningSessionRepository, llm: LlmService):
        self._repo = repo
        self._llm = llm

    async def execute(self, instruction: str, tool_defs_dto: List[ToolDefinitionDto]) -> SessionDto:
        tool_defs = [ToolMapper.to_domain(d) for d in tool_defs_dto]
        session = PlanningSession.create(instruction, tool_defs)

        content, tool_calls, plan = await self._llm.think(session)
        session.add_ai_response(content, tool_calls, plan)

        await self._repo.save(session)
        return SessionMapper.to_dto(session)
