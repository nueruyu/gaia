from gaia.application.planning.planning_agent import PlanningAgent
from gaia.domain.planning.planning_session import PlanningSession
from gaia.domain.planning.planning_session_repository import PlanningSessionRepository


class PlanningSessionService:
    def __init__(
        self,
        planning_agent: PlanningAgent,
        session_repository: PlanningSessionRepository,
    ):
        self._planning_agent = planning_agent
        self._session_repository = session_repository

    async def advance(self, session: PlanningSession) -> None:
        content, tool_calls, plan = await self._planning_agent.think(session)

        if plan:
            session.complete_with_plan(content, plan)
        else:
            session.request_tool_calls(content, tool_calls)

        await self._session_repository.save(session)
