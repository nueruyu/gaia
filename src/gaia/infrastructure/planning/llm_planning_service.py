import json
from typing import List, Optional, Tuple

from gaia.application.ai.ports import Llm
from gaia.application.planning.planning_service import PlanningService
from gaia.domain.ai.values import HumanMessage, ToolCall
from gaia.domain.planning.aggregates import PlanningSession
from gaia.domain.planning.entities import Objective, Plan, Strategy
from gaia.infrastructure.planning.prompts import SYSTEM_PROMPT


class LlmPlanningService(PlanningService):
    def __init__(self, llm: Llm):
        self._llm = llm

    async def think(
        self, session: PlanningSession
    ) -> Tuple[str, List[ToolCall], Optional[Plan]]:
        messages = [HumanMessage(content=SYSTEM_PROMPT), *session.history]

        response = await self._llm.invoke(messages, session.tool_definitions)

        content = response.content
        tool_calls = response.tool_calls

        parsed_plan = None
        if not tool_calls:
            parsed_plan = self._try_parse_plan(content)

        return content, tool_calls, parsed_plan

    def _try_parse_plan(self, content: str) -> Optional[Plan]:
        try:
            cleaned = content.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0]
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0]

            data = json.loads(cleaned)
            return Plan(
                overall_objective=data["overall_objective"],
                objectives=[Objective(**obj) for obj in data["objectives"]],
                strategy=Strategy(**data["strategy"]),
                thought=data.get("thought", ""),
            )
        except Exception:
            return None
