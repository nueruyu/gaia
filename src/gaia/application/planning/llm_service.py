from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from gaia.domain.ai.values import ToolCall
from gaia.domain.planning.aggregates import PlanningSession
from gaia.domain.planning.entities import Plan


class LlmService(ABC):
    @abstractmethod
    async def think(
        self, session: PlanningSession
    ) -> Tuple[str, List[ToolCall], Optional[Plan]]:
        pass
