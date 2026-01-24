from typing import Any, Dict, List

from pydantic import BaseModel


class SubmitToolOutputsRequest(BaseModel):
    tool_outputs: List[Dict[str, Any]]


class CreateSessionRequest(BaseModel):
    instruction: str
    tool_definitions: List[Dict[str, Any]]
    objective_definitions: List[Dict[str, Any]]


class ToolCallDto(BaseModel):
    id: str
    function_name: str
    arguments: str


class ToolOutputDto(BaseModel):
    tool_call_id: str
    output: str


class ToolDefinitionDto(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class ObjectiveDefinitionDto(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
