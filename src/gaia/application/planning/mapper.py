from gaia.application.ai.mapper import AIMapper
from gaia.application.planning.dtos import (
    ObjectiveDefinitionDto,
    PlanDto,
    PlanningSessionDto,
)
from gaia.domain.planning.plan import Plan
from gaia.domain.planning.planning_session import (
    ObjectiveDefinition,
    PlanningSession,
)


class PlanningMapper:
    @staticmethod
    def to_objective_definition(dto: ObjectiveDefinitionDto) -> ObjectiveDefinition:
        return ObjectiveDefinition(
            name=dto.name, description=dto.description, parameters=dto.parameters
        )

    @staticmethod
    def to_planning_session_dto(session: PlanningSession) -> PlanningSessionDto:
        tool_call_dtos = [
            AIMapper.to_tool_call_dto(tc) for tc in session.get_waiting_tool_calls()
        ]

        plan_dto = None
        if session.generated_plan:
            plan_dto = PlanningMapper.to_plan_dto(session.generated_plan)

        return PlanningSessionDto(
            session_id=session.session_id,
            status=session.status.value,
            tool_calls=tool_call_dtos,
            plan=plan_dto,
        )

    @staticmethod
    def to_plan_dto(plan: Plan) -> PlanDto:
        return PlanDto(
            overall_objective=plan.overall_objective,
            objectives=[
                {"type": o.type, "parameters": o.parameters, "priority": o.priority}
                for o in plan.objectives
            ],
            strategy={
                "priority": plan.strategy.priority,
                "engagement": plan.strategy.engagement,
                "retreat_condition": plan.strategy.retreat_condition,
            },
            thought=plan.thought,
        )
