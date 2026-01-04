from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

# --- Common Models ---


class Vector3(BaseModel):
    """
    Represents a 3D vector.
    """

    x: float
    y: float
    z: float


# --- Request Models ---


class CharacterTypeDefinition(BaseModel):
    """
    Static definition of a character type.
    """

    type_id: str = Field(..., description="Unique identifier for the character type.")
    display_name: str = Field(..., description="Display name of the character.")
    threat_level: int = Field(..., description="AI-related threat level assessment.")


class ItemTypeDefinition(BaseModel):
    """
    Static definition of an item type.
    """

    item_id: str = Field(..., description="Unique identifier for the item type.")
    name: str = Field(..., description="Display name of the item.")
    utility: int = Field(..., description="AI-related utility score.")


class GoalDefinition(BaseModel):
    """
    Definition of a goal that an AI agent can pursue.
    """

    name: str = Field(..., description="The name of the goal.")
    description: str = Field(..., description="A description of what the goal entails.")
    parameters: Dict[str, Any] = Field(
        ..., description="Parameters required to execute the goal."
    )


class StaticDefinitions(BaseModel):
    """
    Container for all static game definitions.
    """

    character_types: List[CharacterTypeDefinition]
    item_types: List[ItemTypeDefinition]


class AgentContext(BaseModel):
    """
    Contextual information for the AI agent making the decision.
    """

    agent_character_type: str = Field(
        ..., description="The character type of the agent itself."
    )
    mission_objective: str = Field(
        ..., description="The overall high-level mission objective."
    )


class PlanRequest(BaseModel):
    """
    The complete request body sent from the client to request a plan.
    """

    context: AgentContext
    definitions: StaticDefinitions
    available_goals: List[GoalDefinition]


# --- Response Models ---


class Objective(BaseModel):
    """
    A single objective within a plan, with a priority.
    """

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
    """
    The overall strategy or policy the agent should follow while executing the plan.
    """

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
    """
    The complete plan returned by the server.
    """

    overall_objective: str = Field(
        ..., description="A high-level summary of the plan's goal."
    )
    objectives: List[Objective]
    strategy: Strategy
    thought: str = Field(..., description="The AI's reasoning for creating this plan.")
