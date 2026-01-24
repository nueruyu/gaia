from gaia.application.ai.dto import (
    SubmitToolOutputsRequest,
    ToolDefinitionDto,
    ToolOutputDto,
)
from gaia.application.planning.dtos import (
    PlanningSessionDto,
)
from gaia.application.planning.llm_service import LlmService
from gaia.application.planning.mappers import SessionMapper, ToolMapper
from gaia.domain.planning.repositories import PlanningSessionRepository


class SubmitToolOutputsUseCase:
    def __init__(self, repo: PlanningSessionRepository, llm: LlmService):
        self._repo = repo
        self._llm = llm

    async def execute(
        self, session_id: str, request: SubmitToolOutputsRequest
    ) -> PlanningSessionDto:
        session = await self._repo.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        outputs = [
            ToolMapper.output_to_domain(ToolOutputDto(**o))
            for o in request.tool_outputs
        ]
        tool_defs = [
            ToolMapper.to_domain(ToolDefinitionDto(**td))
            for td in request.tool_definitions
        ]

        session.add_tool_outputs(outputs, tool_defs)

        content, tool_calls, plan = await self._llm.think(session)
        session.add_ai_response(content, tool_calls, plan)

        await self._repo.save(session)
        return SessionMapper.to_dto(session)
