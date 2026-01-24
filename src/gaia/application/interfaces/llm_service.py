from abc import ABC, abstractmethod
from typing import Tuple, List, Optional
from gaia.domain.aggregates import PlanningSession
from gaia.domain.values import ToolCall
from gaia.domain.entities import Plan

class LlmService(ABC):
    @abstractmethod
    async def think(self, session: PlanningSession) -> Tuple[str, List[ToolCall], Optional[Plan]]:
        pass
