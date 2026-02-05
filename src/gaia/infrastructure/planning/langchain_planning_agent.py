import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage as LCAIMessage
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.messages import HumanMessage as LCHumanMessage
from langchain_core.messages import ToolMessage as LCToolMessage

from gaia.application.planning.planning_agent import PlanningAgent
from gaia.domain.ai.message import (
    AIMessage,
    Message,
    MessageType,
    ToolMessage,
)
from gaia.domain.ai.tool import ToolCall, ToolDefinition
from gaia.domain.planning.plan import Objective, Plan, Strategy
from gaia.domain.planning.planning_session import ObjectiveDefinition, PlanningSession
from gaia.infrastructure.planning.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class LangChainPlanningAgent(PlanningAgent):
    def __init__(self, model: BaseChatModel):
        self._model = model

    async def think(
        self, session: PlanningSession
    ) -> Tuple[str, List[ToolCall], Optional[Plan]]:
        logger.info(f"[{session.session_id}] Starting think process...")

        # 1. Prepare System Prompt with Objectives
        system_content = self._build_system_prompt(session.objective_definitions)

        # 2. Convert History
        lc_messages: List[BaseMessage] = [SystemMessage(content=system_content)]
        lc_messages.extend(self._convert_messages(session.history))

        logger.debug(f"[{session.session_id}] Sending messages to LLM: {lc_messages}")

        # 3. Bind Tools
        tools_schema = [self._to_tool_schema(td) for td in session.tool_definitions]
        model = self._model.bind_tools(tools_schema) if tools_schema else self._model

        # 4. Invoke
        response = await model.ainvoke(lc_messages)
        logger.info(f"[{session.session_id}] Received response from LLM: {response}")

        # 5. Parse Response
        content = str(response.content)
        tool_calls = self._extract_tool_calls(response)

        parsed_plan = None
        if not tool_calls:
            parsed_plan = self._try_parse_plan(content)

        logger.info(
            f"[{session.session_id}] Parsed output - Tool Calls: {len(tool_calls)}, Plan Generated: {parsed_plan is not None}"
        )

        return content, tool_calls, parsed_plan

    def _build_system_prompt(
        self, objective_definitions: List[ObjectiveDefinition]
    ) -> str:
        objectives_desc = []
        for obj in objective_definitions:
            props = obj.parameters.get("properties", {})
            param_desc = ", ".join(
                f"{k}: {v.get('type', 'any')}" for k, v in props.items()
            )
            objectives_desc.append(
                f"- Type: '{obj.name}'\n  Desc: {obj.description}\n  Params: {{ {param_desc} }}"
            )

        objectives_str = (
            "\n".join(objectives_desc)
            if objectives_desc
            else "No specific objective types defined."
        )
        return SYSTEM_PROMPT.replace("{{objective_schema}}", objectives_str)

    def _convert_messages(self, messages: List[Message]) -> List[BaseMessage]:
        lc_messages: List[BaseMessage] = []

        for msg in messages:
            if msg.type == MessageType.HUMAN:
                lc_messages.append(LCHumanMessage(content=msg.content))
            elif msg.type == MessageType.AI:
                if isinstance(msg, AIMessage):
                    tc_dicts: List[Dict[str, Any]] = []
                    for tc in msg.tool_calls:
                        tc_dicts.append(
                            {
                                "id": tc.id,
                                "name": tc.function_name,
                                "args": tc.arguments,
                            }
                        )
                    lc_messages.append(
                        LCAIMessage(content=msg.content, tool_calls=tc_dicts)
                    )
            elif msg.type == MessageType.TOOL:
                if isinstance(msg, ToolMessage):
                    lc_messages.append(
                        LCToolMessage(
                            tool_call_id=msg.tool_call_id, content=msg.content
                        )
                    )

        return lc_messages

    def _to_tool_schema(self, td: ToolDefinition) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": td.name,
                "description": td.description,
                "parameters": td.parameters,
            },
        }

    def _extract_tool_calls(self, response: Any) -> List[ToolCall]:
        tool_calls: List[ToolCall] = []
        response_tool_calls = getattr(response, "tool_calls", None)
        if response_tool_calls:
            for tc in response_tool_calls:
                tc_id = tc.get("id", "")
                tool_calls.append(
                    ToolCall(
                        id=str(tc_id) if tc_id else "",
                        function_name=tc["name"],
                        arguments=tc["args"],
                    )
                )
        return tool_calls

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
        except Exception as e:
            logger.warning(f"Failed to parse plan: {e}", exc_info=True)
            return None
