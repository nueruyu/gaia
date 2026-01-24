from typing import List
from gaia.application.interfaces.llm_service import LlmService
from gaia.domain.repositories import PlanningSessionRepository
from gaia.application.dtos import SessionDto, ToolOutputDto, ToolDefinitionDto
from gaia.application.mappers import SessionMapper, ToolMapper

class SubmitToolOutputsUseCase:
    def __init__(self, repo: PlanningSessionRepository, llm: LlmService):
        self._repo = repo
        self._llm = llm

    async def execute(self, session_id: str, outputs_dto: List[ToolOutputDto], tool_defs_dto: List[ToolDefinitionDto]) -> SessionDto:
        session = await self._repo.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        outputs = [ToolMapper.output_to_domain(o) for o in outputs_dto]
        tool_defs = [ToolMapper.to_domain(d) for d in tool_defs_dto]

        session.add_tool_outputs(outputs, tool_defs)

        content, tool_calls, plan = await self._llm.think(session)
        session.add_ai_response(content, tool_calls, plan)

        await self._repo.save(session)
        return SessionMapper.to_dto(session)
