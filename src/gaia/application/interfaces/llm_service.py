from abc import ABC, abstractmethod
from gaia.domain.entities import Plan
from gaia.application.dtos import PlanRequest


class LlmService(ABC):
    """An abstract interface for a service that can generate game AI plans."""

    @abstractmethod
    def create_plan(self, request: PlanRequest) -> Plan:
        """
        Generates a strategic plan based on the provided request data.

        Args:
            request: The data transfer object containing all necessary context.

        Returns:
            A Plan domain entity.
        """
        pass
