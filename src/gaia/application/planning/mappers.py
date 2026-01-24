import json

from gaia.application.ai.dto import ToolCallDto, ToolDefinitionDto, ToolOutputDto
from gaia.application.planning.dtos import (
    PlanDto,
    PlanningSessionDto,
)
from gaia.domain.ai.values import AIMessage, ToolDefinition, ToolOutput
from gaia.domain.planning.aggregates import (
    PlanningSession,
    SessionStatus,
)


class ToolMapper:
    @staticmethod
    def to_domain(dto: ToolDefinitionDto) -> ToolDefinition:
        return ToolDefinition(
            name=dto.name, description=dto.description, parameters=dto.parameters
        )

    @staticmethod
    def output_to_domain(dto: ToolOutputDto) -> ToolOutput:
        return ToolOutput(tool_call_id=dto.tool_call_id, output=dto.output)


class SessionMapper:
    @staticmethod
    def to_dto(session: PlanningSession) -> PlanningSessionDto:
        tool_calls_dto = None

        if session.status == SessionStatus.WAITING_FOR_TOOL:
            last_msg = session.history[-1]
            if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
                tool_calls_dto = [
                    ToolCallDto(
                        id=tc.id,
                        function_name=tc.function_name,
                        arguments=json.dumps(tc.arguments),
                    )
                    for tc in last_msg.tool_calls
                ]

        plan_dto = None
        if session.generated_plan:
            p = session.generated_plan
            plan_dto = PlanDto(
                overall_objective=p.overall_objective,
                objectives=[
                    {"type": o.type, "parameters": o.parameters, "priority": o.priority}
                    for o in p.objectives
                ],
                strategy={
                    "priority": p.strategy.priority,
                    "engagement": p.strategy.engagement,
                    "retreat_condition": p.strategy.retreat_condition,
                },
                thought=p.thought,
            )

        return PlanningSessionDto(
            session_id=session.session_id,
            status=session.status.value,
            tool_calls=tool_calls_dto,
            plan=plan_dto,
        )
