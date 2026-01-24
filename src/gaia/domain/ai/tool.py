from dataclasses import dataclass
from typing import Any, Dict


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
class ObjectiveDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]
