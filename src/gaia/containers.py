from dependency_injector import containers, providers
from langchain_core.language_models.chat_models import BaseChatModel

from gaia.application.planning.create_session import CreateSessionUseCase
from gaia.application.planning.llm_service import LlmService
from gaia.application.planning.submit_tool_outputs import SubmitToolOutputsUseCase
from gaia.config import Settings
from gaia.domain.planning.repositories import PlanningSessionRepository
from gaia.infrastructure.llm.gemini_llm import create_gemini_llm
from gaia.infrastructure.llm.langchain_service import LangChainLlmService
from gaia.infrastructure.llm.mock_llm import MockChatModel
from gaia.infrastructure.persistence.langgraph_repository import LangGraphRepository


def _create_llm_model(settings: Settings) -> BaseChatModel:
    if settings.LLM_MODE == "MOCK":
        return MockChatModel()
    elif settings.LLM_MODE == "GEMINI":
        return create_gemini_llm()
    else:
        raise ValueError(f"Unknown LLM_MODE: {settings.LLM_MODE}")


def _create_planning_repo(settings: Settings) -> LangGraphRepository:
    return LangGraphRepository(db_path=settings.DB_PATH)


def _create_llm_service(llm: BaseChatModel) -> LangChainLlmService:
    return LangChainLlmService(llm=llm)


def _create_session_use_case(
    repo: PlanningSessionRepository, llm: LlmService
) -> CreateSessionUseCase:
    return CreateSessionUseCase(repo=repo, llm=llm)


def _create_submit_tool_outputs_use_case(
    repo: PlanningSessionRepository, llm: LlmService
) -> SubmitToolOutputsUseCase:
    return SubmitToolOutputsUseCase(repo=repo, llm=llm)


class Container(containers.DeclarativeContainer):
    config: providers.Singleton[Settings] = providers.Singleton(Settings)

    llm_model: providers.Singleton[BaseChatModel] = providers.Singleton(
        _create_llm_model, settings=config
    )

    planning_repo: providers.Singleton[LangGraphRepository] = providers.Singleton(
        _create_planning_repo, settings=config
    )

    llm_service: providers.Singleton[LangChainLlmService] = providers.Singleton(
        _create_llm_service, llm=llm_model
    )

    create_session_use_case: providers.Factory[CreateSessionUseCase] = providers.Factory(
        _create_session_use_case, repo=planning_repo, llm=llm_service
    )

    submit_tool_outputs_use_case: providers.Factory[SubmitToolOutputsUseCase] = (
        providers.Factory(
            _create_submit_tool_outputs_use_case, repo=planning_repo, llm=llm_service
        )
    )
