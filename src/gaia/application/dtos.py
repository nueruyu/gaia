from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ToolDefinitionDto(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class ToolOutputDto(BaseModel):
    tool_call_id: str
    output: str


class ToolCallDto(BaseModel):
    id: str
    function_name: str
    arguments: str


class PlanDto(BaseModel):
    overall_objective: str
    objectives: List[Dict[str, Any]]
    strategy: Dict[str, Any]
    thought: str


class SessionDto(BaseModel):
    session_id: str
    status: str
    tool_calls: Optional[List[ToolCallDto]] = None
    plan: Optional[PlanDto] = None
    error_message: Optional[str] = None
