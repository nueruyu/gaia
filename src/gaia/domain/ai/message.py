from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from gaia.domain.ai.tool import ToolCall


class MessageType(str, Enum):
    HUMAN = "human"
    AI = "ai"
    TOOL = "tool"


@dataclass
class Message:
    type: MessageType
    content: str


@dataclass
class AIMessage(Message):
    tool_calls: List[ToolCall] = field(default_factory=list)

    def __init__(self, content: str, tool_calls: Optional[List[ToolCall]] = None):
        self.type = MessageType.AI
        self.content = content
        self.tool_calls = tool_calls if tool_calls is not None else []


@dataclass
class HumanMessage(Message):
    def __init__(self, content: str):
        self.type = MessageType.HUMAN
        self.content = content


@dataclass
class ToolMessage(Message):
    tool_call_id: str

    def __init__(self, tool_call_id: str, content: str):
        self.type = MessageType.TOOL
        self.tool_call_id = tool_call_id
        self.content = content
