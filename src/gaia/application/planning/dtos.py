from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from gaia.application.ai.dto import ToolCallDto


class PlanDto(BaseModel):
    overall_objective: str
    objectives: List[Dict[str, Any]]
    strategy: Dict[str, Any]
    thought: str


class PlanningSessionDto(BaseModel):
    session_id: str
    status: str
    tool_calls: Optional[List[ToolCallDto]] = None
    plan: Optional[PlanDto] = None
    error_message: Optional[str] = None
