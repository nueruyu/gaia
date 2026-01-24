from typing import Any, List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage as LCAIMessage
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage as LCHumanMessage
from langchain_core.messages import ToolMessage as LCToolMessage

from gaia.application.ai.ports import Llm
from gaia.domain.ai.values import (
    AIMessage,
    Message,
    MessageType,
    ToolCall,
    ToolDefinition,
    ToolMessage,
)


class LangChainLlm(Llm):
    def __init__(self, model: BaseChatModel):
        self._model = model

    async def invoke(
        self, messages: List[Message], tool_definitions: List[ToolDefinition]
    ) -> AIMessage:
        lc_messages = self._convert_messages(messages)
        tools_schema = [self._to_tool_schema(td) for td in tool_definitions]

        model = self._model.bind_tools(tools_schema) if tools_schema else self._model

        response = await model.ainvoke(lc_messages)
        return self._convert_response(response)

    def _convert_messages(self, messages: List[Message]) -> List[BaseMessage]:
        lc_messages: List[BaseMessage] = []

        for msg in messages:
            if msg.type == MessageType.HUMAN:
                lc_messages.append(LCHumanMessage(content=msg.content))
            elif msg.type == MessageType.AI:
                if isinstance(msg, AIMessage):
                    tc_dicts: List[Any] = []
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

    def _convert_response(self, response: Any) -> AIMessage:
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

        return AIMessage(content=content, tool_calls=tool_calls)

    def _to_tool_schema(self, td: ToolDefinition) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": td.name,
                "description": td.description,
                "parameters": td.parameters,
            },
        }
