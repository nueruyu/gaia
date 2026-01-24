from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

class MessageType(str, Enum):
    HUMAN = "human"
    AI = "ai"
    TOOL = "tool"

class SessionStatus(str, Enum):
    THINKING = "Thinking"
    WAITING_FOR_TOOL = "WaitingForTool"
    COMPLETED = "Completed"

@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]

@dataclass
class ToolCall:
    id: str
    function_name: str
    arguments: Dict[str, Any]

@dataclass
class ToolOutput:
    tool_call_id: str
    output: str

@dataclass
class DomainMessage:
    type: MessageType
    content: str

@dataclass
class AIMessage(DomainMessage):
    tool_calls: List[ToolCall] = field(default_factory=list)

    def __init__(self, content: str, tool_calls: Optional[List[ToolCall]] = None):
        self.type = MessageType.AI
        self.content = content
        self.tool_calls = tool_calls if tool_calls is not None else []

@dataclass
class HumanMessage(DomainMessage):
    def __init__(self, content: str):
        self.type = MessageType.HUMAN
        self.content = content

@dataclass
class ToolMessage(DomainMessage):
    tool_call_id: str

    def __init__(self, tool_call_id: str, content: str):
        self.type = MessageType.TOOL
        self.tool_call_id = tool_call_id
        self.content = content
