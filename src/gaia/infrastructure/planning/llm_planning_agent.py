import json
from typing import List, Optional, Tuple

from gaia.application.planning.planning_agent import PlanningAgent
from gaia.domain.ai.message import HumanMessage
from gaia.domain.ai.tool import ToolCall
from gaia.domain.planning.plan import Objective, Plan, Strategy
from gaia.domain.planning.planning_session import PlanningSession
from gaia.infrastructure.llms.llm import Llm
from gaia.infrastructure.planning.prompts import SYSTEM_PROMPT


class LlmPlanningAgent(PlanningAgent):
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
