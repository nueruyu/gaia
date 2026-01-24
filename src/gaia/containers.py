from dependency_injector import containers, providers

from gaia.application.planning.create_session_use_case import CreateSessionUseCase
from gaia.application.planning.planning_service import PlanningService
from gaia.application.planning.submit_tool_outputs_use_case import (
    SubmitToolOutputsUseCase,
)
from gaia.config import Settings
from gaia.domain.planning.planning_session_repository import PlanningSessionRepository
from gaia.infrastructure.planning.langgraph_planning_session_repository import (
    LangGraphPlanningSessionRepository,
)
from gaia.infrastructure.planning.llm_factory import create_planning_llm
from gaia.infrastructure.planning.llm_planning_service import LlmPlanningService


def _create_planning_repo(settings: Settings) -> LangGraphPlanningSessionRepository:
    return LangGraphPlanningSessionRepository(db_path=settings.DB_PATH)


def _create_llm_service(settings: Settings) -> LlmPlanningService:
    llm = create_planning_llm(settings)
    return LlmPlanningService(llm=llm)


def _create_session_use_case(
    repo: PlanningSessionRepository, llm: PlanningService
) -> CreateSessionUseCase:
    return CreateSessionUseCase(session_repository=repo, planning_service=llm)


def _create_submit_tool_outputs_use_case(
    repo: PlanningSessionRepository, llm: PlanningService
) -> SubmitToolOutputsUseCase:
    return SubmitToolOutputsUseCase(session_repository=repo, planning_service=llm)


class Container(containers.DeclarativeContainer):
    config: providers.Singleton[Settings] = providers.Singleton(Settings)

    planning_repo: providers.Singleton[LangGraphPlanningSessionRepository] = (
        providers.Singleton(_create_planning_repo, settings=config)
    )

    llm_service: providers.Singleton[LlmPlanningService] = providers.Singleton(
        _create_llm_service, settings=config
    )

    create_session_use_case: providers.Factory[CreateSessionUseCase] = (
        providers.Factory(_create_session_use_case, repo=planning_repo, llm=llm_service)
    )

    submit_tool_outputs_use_case: providers.Factory[SubmitToolOutputsUseCase] = (
        providers.Factory(
            _create_submit_tool_outputs_use_case, repo=planning_repo, llm=llm_service
        )
    )
