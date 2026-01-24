from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

# --- Common Models ---


class Vector3(BaseModel):
    x: float
    y: float
    z: float


# --- Static Knowledge Entities ---


class CharacterTypeDefinition(BaseModel):
    type_id: str = Field(..., description="Unique identifier for the character type.")
    display_name: str = Field(..., description="Display name of the character.")
    threat_level: int = Field(..., description="AI-related threat level assessment.")


class ItemTypeDefinition(BaseModel):
    item_id: str = Field(..., description="Unique identifier for the item type.")
    name: str = Field(..., description="Display name of the item.")
    utility: int = Field(..., description="AI-related utility score.")


# --- Plan Entities ---


class Objective(BaseModel):
    type: str = Field(
        ..., description="The type of objective (e.g., 'DefeatCharacter')."
    )
    parameters: Dict[str, Any] = Field(
        ..., description="Parameters for this objective."
    )
    priority: int = Field(
        ..., description="Priority of this objective, higher is more important."
    )


class Strategy(BaseModel):
    priority: Literal["Survival", "Aggressive", "Stealth"] = Field(
        ..., description="The main strategic focus."
    )
    engagement: Literal["EngageAll", "AvoidUnnecessaryFights"] = Field(
        ..., description="Rules of engagement."
    )
    retreat_condition: Dict[str, Any] = Field(
        ..., description="Conditions under which to retreat."
    )


class Plan(BaseModel):
    overall_objective: str = Field(
        ..., description="A high-level summary of the plan's goal."
    )
    objectives: List[Objective]
    strategy: Strategy
    thought: str = Field(..., description="The AI's reasoning for creating this plan.")
