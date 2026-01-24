from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from gaia.domain.ai.tool import ToolCall
from gaia.domain.planning.plan import Plan
from gaia.domain.planning.planning_session import PlanningSession


class PlanningAgent(ABC):
    @abstractmethod
    async def think(
        self, session: PlanningSession
    ) -> Tuple[str, List[ToolCall], Optional[Plan]]:
        pass
