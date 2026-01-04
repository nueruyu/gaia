from pydantic import BaseModel, Field
from typing import List, Dict, Any
from gaia.domain.entities import CharacterTypeDefinition, ItemTypeDefinition

# --- DTOs for CreatePlanUseCase ---


class GoalDefinition(BaseModel):
    name: str = Field(..., description="The name of the goal.")
    description: str = Field(..., description="A description of what the goal entails.")
    parameters: Dict[str, Any] = Field(
        ..., description="Parameters required to execute the goal."
    )


class StaticDefinitions(BaseModel):
    character_types: List[CharacterTypeDefinition]
    item_types: List[ItemTypeDefinition]


class AgentContext(BaseModel):
    agent_character_type: str = Field(
        ..., description="The character type of the agent itself."
    )
    mission_objective: str = Field(
        ..., description="The overall high-level mission objective."
    )


class PlanRequest(BaseModel):
    context: AgentContext
    definitions: StaticDefinitions
    available_goals: List[GoalDefinition]
