import json
from typing import List, Optional, Tuple

from gaia.application.planning.planning_agent import PlanningAgent
from gaia.domain.ai.message import HumanMessage
from gaia.domain.ai.tool import ObjectiveDefinition, ToolCall
from gaia.domain.planning.plan import Objective, Plan, Strategy
from gaia.domain.planning.planning_session import PlanningSession
from gaia.infrastructure.llms.llm import Llm
from gaia.infrastructure.planning.prompts import SYSTEM_PROMPT_TEMPLATE


class LlmPlanningAgent(PlanningAgent):
    def __init__(self, llm: Llm):
        self._llm = llm

    async def think(
        self, session: PlanningSession
    ) -> Tuple[str, List[ToolCall], Optional[Plan]]:
        objective_schema = self._format_objective_schema(session.objective_definitions)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(objective_schema=objective_schema)
        messages = [HumanMessage(content=system_prompt), *session.history]

        response = await self._llm.invoke(messages, session.tool_definitions)

        content = response.content
        tool_calls = response.tool_calls

        parsed_plan = None
        if not tool_calls:
            parsed_plan = self._try_parse_plan(content)

        return content, tool_calls, parsed_plan

    def _format_objective_schema(
        self, objective_definitions: List[ObjectiveDefinition]
    ) -> str:
        if not objective_definitions:
            return "No specific objective types defined."

        lines = []
        for obj_def in objective_definitions:
            lines.append(f"- **{obj_def.name}**: {obj_def.description}")
            lines.append(f"  Parameters: {json.dumps(obj_def.parameters)}")
        return "\n".join(lines)

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
