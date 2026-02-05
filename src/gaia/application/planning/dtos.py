from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from gaia.application.ai.dto import ToolCallDto


class PlanDto(BaseModel):
    overall_objective: str
    objectives: List[Dict[str, Any]]
    strategy: Dict[str, Any]
    thought: str


class PlanningSessionDto(BaseModel):
    session_id: str
    status: str
    tool_calls: List[ToolCallDto] = Field(default_factory=list)
    plan: Optional[PlanDto] = None
    error_message: Optional[str] = None


class ObjectiveDefinitionDto(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class CreateSessionRequest(BaseModel):
    instruction: str
    tool_definitions: List[Dict[str, Any]]
    objective_definitions: List[Dict[str, Any]]
