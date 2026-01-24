from abc import ABC, abstractmethod
from typing import List

from gaia.domain.ai.values import AIMessage, Message, ToolDefinition


class Llm(ABC):
    @abstractmethod
    async def invoke(
        self, messages: List[Message], tool_definitions: List[ToolDefinition]
    ) -> AIMessage:
        pass
