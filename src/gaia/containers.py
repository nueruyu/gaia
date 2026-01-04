from dependency_injector import containers, providers
from langchain_core.language_models.chat_models import BaseChatModel

from gaia.application.interfaces.llm_service import LlmService
from gaia.application.use_cases.create_plan import CreatePlanUseCase
from gaia.infrastructure.llm.gemini_llm import create_gemini_llm
from gaia.infrastructure.llm.langchain_service import LangChainLlmService
from gaia.infrastructure.llm.mock_llm import MockChatModel


class Container(containers.DeclarativeContainer):
    """The DI container for the 'gaia' application."""

    # --- Configuration ---
    # Declare a configuration provider. The actual values will be
    # provided from the outside (by main.py).
    config = providers.Configuration()

    # --- Infrastructure Layer: LLM Models ---
    mock_llm_provider = providers.Singleton(MockChatModel)
    gemini_llm_provider = providers.Singleton(create_gemini_llm)

    # --- Infrastructure Layer: Selector ---
    # This provider selects the correct LLM model based on the LLM_MODE config.
    llm_model: providers.Selector[BaseChatModel] = providers.Selector(
        config.LLM_MODE,
        MOCK=mock_llm_provider,
        GEMINI=gemini_llm_provider,
    )

    # --- Infrastructure Layer: Main Service ---
    llm_service: providers.Singleton[LlmService] = providers.Singleton(
        LangChainLlmService,
        llm=llm_model,
    )

    # --- Application Layer ---
    create_plan_use_case: providers.Factory[CreatePlanUseCase] = providers.Factory(
        CreatePlanUseCase,
        llm_service=llm_service,
    )
