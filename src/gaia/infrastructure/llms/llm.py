from abc import ABC, abstractmethod
from typing import List

from gaia.domain.ai.message import AIMessage, Message
from gaia.domain.ai.tool import ToolDefinition


class Llm(ABC):
    @abstractmethod
    async def invoke(
        self, messages: List[Message], tool_definitions: List[ToolDefinition]
    ) -> AIMessage:
        pass
