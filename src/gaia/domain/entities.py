from dataclasses import dataclass
from typing import List, Dict, Any, Literal


@dataclass
class Objective:
    type: str
    parameters: Dict[str, Any]
    priority: int


@dataclass
class Strategy:
    priority: Literal["Survival", "Aggressive", "Stealth"]
    engagement: Literal["EngageAll", "AvoidUnnecessaryFights"]
    retreat_condition: Dict[str, Any]


@dataclass
class Plan:
    overall_objective: str
    objectives: List[Objective]
    strategy: Strategy
    thought: str
