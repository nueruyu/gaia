from gaia.application.ai.dto import (
    SubmitToolOutputsRequest,
    ToolDefinitionDto,
    ToolOutputDto,
)
from gaia.application.planning.dtos import (
    PlanningSessionDto,
)
from gaia.application.planning.mappers import SessionMapper, ToolMapper
from gaia.application.planning.planning_service import PlanningService
from gaia.domain.planning.planning_session_repository import PlanningSessionRepository


class SubmitToolOutputsUseCase:
    def __init__(
        self,
        session_repository: PlanningSessionRepository,
        planning_service: PlanningService,
    ):
        self._session_repository = session_repository
        self._planning_service = planning_service

    async def execute(
        self, session_id: str, request: SubmitToolOutputsRequest
    ) -> PlanningSessionDto:
        session = await self._session_repository.get(session_id)
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

        content, tool_calls, plan = await self._planning_service.think(session)
        session.add_ai_response(content, tool_calls, plan)

        await self._session_repository.save(session)
        return SessionMapper.to_dto(session)
