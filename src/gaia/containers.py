from dependency_injector import containers, providers

from gaia.application.use_cases.create_plan import CreatePlanUseCase
from gaia.application.interfaces.llm_service import LlmService
from gaia.infrastructure.llm.langchain_service import LangChainLlmService


class Container(containers.DeclarativeContainer):
    """
    The dependency injection container for the 'gaia' application.
    It wires interfaces to concrete implementations.
    """

    # Configuration (if any) would go here

    # --- Infrastructure Layer ---
    # Provide a singleton instance of our LangChainLlmService implementation
    # whenever an LlmService is requested.
    llm_service: providers.Singleton[LlmService] = providers.Singleton(
        LangChainLlmService
    )

    # --- Application Layer ---
    # Provide a new instance of CreatePlanUseCase every time it's requested.
    # The container automatically injects the 'llm_service' dependency.
    create_plan_use_case: providers.Factory[CreatePlanUseCase] = providers.Factory(
        CreatePlanUseCase,
        llm_service=llm_service,
    )
