from abc import ABC, abstractmethod
from typing import Optional
from gaia.domain.aggregates import PlanningSession

class PlanningSessionRepository(ABC):
    @abstractmethod
    async def save(self, session: PlanningSession) -> None:
        pass

    @abstractmethod
    async def get(self, session_id: str) -> Optional[PlanningSession]:
        pass

    @abstractmethod
    async def initialize(self) -> None:
        pass
