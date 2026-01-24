from typing import List, Dict, Any
from pydantic import BaseModel
from gaia.application.dtos import SessionDto


class CreateSessionRequest(BaseModel):
    instruction: str
    tool_definitions: List[Dict[str, Any]]


class SubmitToolOutputsRequest(BaseModel):
    tool_outputs: List[Dict[str, Any]]
    tool_definitions: List[Dict[str, Any]]


SessionResponse = SessionDto
