from gaia.domain.entities import Plan
from gaia.application.dtos import PlanRequest
from gaia.application.interfaces.llm_service import LlmService


class CreatePlanUseCase:
    """Use case for creating a strategic plan for a game agent."""

    def __init__(self, llm_service: LlmService):
        self._llm_service = llm_service

    def execute(self, request: PlanRequest) -> Plan:
        """
        Executes the plan creation process.

        Args:
            request: The request DTO containing agent and world context.

        Returns:
            The generated Plan entity.
        """
        # In a more complex scenario, this use case could orchestrate
        # multiple services, repositories, or perform business logic
        # before and after calling the external service.
        plan = self._llm_service.create_plan(request)
        return plan
