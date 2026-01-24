from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from gaia.domain.ai.message import (
    AIMessage,
    HumanMessage,
    Message,
    ToolMessage,
)
from gaia.domain.ai.tool import (
    ObjectiveDefinition,
    ToolCall,
    ToolDefinition,
    ToolOutput,
)
from gaia.domain.planning.exceptions import PlanningError
from gaia.domain.planning.plan import Plan


class SessionStatus(str, Enum):
    THINKING = "thinking"
    WAITING_FOR_TOOL = "waiting_for_tool"
    COMPLETED = "completed"


@dataclass
class PlanningSession:
    session_id: str
    history: List[Message]
    status: SessionStatus
    tool_definitions: List[ToolDefinition]
    objective_definitions: List[ObjectiveDefinition]
    generated_plan: Optional[Plan] = None

    @classmethod
    def create(
        cls,
        instruction: str,
        tool_definitions: List[ToolDefinition],
        objective_definitions: List[ObjectiveDefinition],
    ):
        return cls(
            session_id=str(uuid4()),
            history=[HumanMessage(content=instruction)],
            status=SessionStatus.THINKING,
            tool_definitions=tool_definitions,
            objective_definitions=objective_definitions,
        )

    def request_tool_calls(self, content: str, tool_calls: List[ToolCall]) -> None:
        if self.status != SessionStatus.THINKING:
            raise PlanningError(
                f"Status mismatch: Expected THINKING, got {self.status}"
            )
        if not tool_calls:
            raise PlanningError("tool_calls must not be empty")

        self.history.append(AIMessage(content=content, tool_calls=tool_calls))
        self.status = SessionStatus.WAITING_FOR_TOOL

    def complete_with_plan(self, content: str, plan: Plan) -> None:
        if self.status != SessionStatus.THINKING:
            raise PlanningError(
                f"Status mismatch: Expected THINKING, got {self.status}"
            )

        self.history.append(AIMessage(content=content, tool_calls=[]))
        self.generated_plan = plan
        self.status = SessionStatus.COMPLETED

    def add_tool_outputs(
        self,
        outputs: List[ToolOutput],
    ):
        if self.status != SessionStatus.WAITING_FOR_TOOL:
            raise PlanningError("Session is not waiting for tool outputs.")

        waiting_tool_calls = self.get_waiting_tool_calls()
        if not waiting_tool_calls:
            raise PlanningError("No active tool calls found in history.")

        requested_ids = {tc.id for tc in waiting_tool_calls}
        for output in outputs:
            if output.tool_call_id not in requested_ids:
                raise PlanningError(f"Unexpected tool output id: {output.tool_call_id}")

            self.history.append(
                ToolMessage(tool_call_id=output.tool_call_id, content=output.output)
            )

        self.status = SessionStatus.THINKING

    def get_waiting_tool_calls(self) -> list[ToolCall]:
        if self.status != SessionStatus.WAITING_FOR_TOOL:
            return []
        last_msg = self.history[-1]
        if not isinstance(last_msg, AIMessage):
            return []

        return last_msg.tool_calls
