import json
from typing import Any, List, Optional, Tuple

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage as LCAIMessage,
)
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
)
from langchain_core.messages import (
    HumanMessage as LCHumanMessage,
)
from langchain_core.messages import (
    ToolMessage as LCToolMessage,
)

from gaia.application.interfaces.llm_service import LlmService
from gaia.domain.aggregates import PlanningSession
from gaia.domain.entities import Objective, Plan, Strategy
from gaia.domain.values import AIMessage, MessageType, ToolCall, ToolMessage
from gaia.infrastructure.llm.prompts import SYSTEM_PROMPT


class LangChainLlmService(LlmService):
    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    async def think(
        self, session: PlanningSession
    ) -> Tuple[str, List[ToolCall], Optional[Plan]]:
        messages: List[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]

        for msg in session.history:
            if msg.type == MessageType.HUMAN:
                messages.append(LCHumanMessage(content=msg.content))
            elif msg.type == MessageType.AI:
                if isinstance(msg, AIMessage):
                    tc_dicts: List[Any] = []
                    for tc in msg.tool_calls:
                        tc_dicts.append(
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function_name,
                                    "arguments": json.dumps(tc.arguments),
                                },
                            }
                        )
                    messages.append(
                        LCAIMessage(content=msg.content, tool_calls=tc_dicts)
                    )
            elif msg.type == MessageType.TOOL:
                if isinstance(msg, ToolMessage):
                    messages.append(
                        LCToolMessage(
                            tool_call_id=msg.tool_call_id, content=msg.content
                        )
                    )

        tools_schema = [self._to_tool_schema(td) for td in session.tool_definitions]
        model = self._llm.bind_tools(tools_schema) if tools_schema else self._llm

        response = await model.ainvoke(messages)
        content = str(response.content)

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

        parsed_plan = None
        if not tool_calls:
            parsed_plan = self._try_parse_plan(content)

        return content, tool_calls, parsed_plan

    def _to_tool_schema(self, td: Any) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": td.name,
                "description": td.description,
                "parameters": td.parameters,
            },
        }

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
