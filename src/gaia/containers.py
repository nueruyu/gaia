from dependency_injector import containers, providers
from langchain_core.language_models.chat_models import BaseChatModel

from gaia.config import Settings
from gaia.infrastructure.llm.gemini_llm import create_gemini_llm
from gaia.infrastructure.llm.mock_llm import MockChatModel
from gaia.infrastructure.llm.langchain_service import LangChainLlmService
from gaia.infrastructure.persistence.langgraph_repository import LangGraphRepository
from gaia.application.use_cases.create_session import CreateSessionUseCase
from gaia.application.use_cases.submit_tool_outputs import SubmitToolOutputsUseCase


class Container(containers.DeclarativeContainer):
    config: providers.Singleton[Settings] = providers.Singleton(Settings)

    mock_llm_provider = providers.Singleton(MockChatModel)
    gemini_llm_provider = providers.Singleton(create_gemini_llm)

    llm_model: providers.Selector[BaseChatModel] = providers.Selector(
        config.provided.LLM_MODE,
        MOCK=mock_llm_provider,
        GEMINI=gemini_llm_provider,
    )

    planning_repo = providers.Singleton(
        LangGraphRepository, db_path=config.provided.DB_PATH
    )

    llm_service = providers.Singleton(LangChainLlmService, llm=llm_model)

    create_session_use_case = providers.Factory(
        CreateSessionUseCase, repo=planning_repo, llm=llm_service
    )

    submit_tool_outputs_use_case = providers.Factory(
        SubmitToolOutputsUseCase, repo=planning_repo, llm=llm_service
    )
