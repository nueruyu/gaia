from dependency_injector import containers, providers

from gaia.application.planning.create_session_use_case import CreateSessionUseCase
from gaia.application.planning.planning_session_service import PlanningSessionService
from gaia.application.planning.submit_tool_outputs_use_case import (
    SubmitToolOutputsUseCase,
)
from gaia.config import Settings
from gaia.infrastructure.planning.langgraph_planning_session_repository import (
    LangGraphPlanningSessionRepository,
)
from gaia.infrastructure.planning.llm_factory import create_planning_llm
from gaia.infrastructure.planning.llm_planning_agent import LlmPlanningAgent


def _create_planning_repo(settings: Settings) -> LangGraphPlanningSessionRepository:
    return LangGraphPlanningSessionRepository(db_path=settings.DB_PATH)


def _create_planning_agent(settings: Settings) -> LlmPlanningAgent:
    llm = create_planning_llm(settings)
    return LlmPlanningAgent(llm=llm)


class Container(containers.DeclarativeContainer):
    config: providers.Singleton[Settings] = providers.Singleton(Settings)

    planning_repo: providers.Singleton[LangGraphPlanningSessionRepository] = (
        providers.Singleton(_create_planning_repo, settings=config)
    )

    planning_agent: providers.Singleton[LlmPlanningAgent] = providers.Singleton(
        _create_planning_agent, settings=config
    )

    planning_session_service: providers.Singleton[PlanningSessionService] = (
        providers.Singleton(
            PlanningSessionService,
            planning_agent=planning_agent,
            session_repository=planning_repo,
        )
    )

    create_session_use_case: providers.Factory[CreateSessionUseCase] = providers.Factory(
        CreateSessionUseCase,
        planning_session_service=planning_session_service,
    )

    submit_tool_outputs_use_case: providers.Factory[SubmitToolOutputsUseCase] = (
        providers.Factory(
            SubmitToolOutputsUseCase,
            session_repository=planning_repo,
            planning_session_service=planning_session_service,
        )
    )
