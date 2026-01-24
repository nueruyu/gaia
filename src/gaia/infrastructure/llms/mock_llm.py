from typing import List, Optional

from gaia.domain.ai.message import AIMessage, Message
from gaia.domain.ai.tool import ToolCall, ToolDefinition
from gaia.infrastructure.llms.llm import Llm


class MockLlm(Llm):
    def __init__(
        self,
        content: str = "",
        tool_calls: Optional[List[ToolCall]] = None,
    ):
        self._content = content
        self._tool_calls = tool_calls if tool_calls is not None else []

    async def invoke(
        self, _messages: List[Message], _tool_definitions: List[ToolDefinition]
    ) -> AIMessage:
        return AIMessage(content=self._content, tool_calls=self._tool_calls)
