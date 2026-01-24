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
from gaia.domain.ai.tool import ToolCall, ToolDefinition, ToolOutput
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
    generated_plan: Optional[Plan] = None

    @classmethod
    def create(
        cls,
        instruction: str,
        tool_definitions: List[ToolDefinition],
    ):
        return cls(
            session_id=str(uuid4()),
            history=[HumanMessage(content=instruction)],
            status=SessionStatus.THINKING,
            tool_definitions=tool_definitions,
        )

    def add_ai_response(
        self,
        content: str,
        tool_calls: List[ToolCall],
        parsed_plan: Optional[Plan],
    ):
        if self.status != SessionStatus.THINKING:
            raise RuntimeError(f"Status mismatch: Expected THINKING, got {self.status}")

        self.history.append(AIMessage(content=content, tool_calls=tool_calls))

        if parsed_plan:
            self.generated_plan = parsed_plan
            self.status = SessionStatus.COMPLETED
        elif tool_calls:
            self.status = SessionStatus.WAITING_FOR_TOOL
        else:
            raise PlanningError(
                "LLM response must contain either tool calls or a valid plan JSON."
            )

    def add_tool_outputs(
        self,
        outputs: List[ToolOutput],
        new_definitions: List[ToolDefinition],
    ):
        if self.status != SessionStatus.WAITING_FOR_TOOL:
            raise RuntimeError("Session is not waiting for tool outputs.")

        last_msg = self.history[-1]
        if not isinstance(last_msg, AIMessage) or not last_msg.tool_calls:
            raise PlanningError("No active tool calls found in history.")

        requested_ids = {tc.id for tc in last_msg.tool_calls}
        for output in outputs:
            if output.tool_call_id not in requested_ids:
                raise PlanningError(f"Unexpected tool output id: {output.tool_call_id}")

            self.history.append(
                ToolMessage(tool_call_id=output.tool_call_id, content=output.output)
            )

        self.tool_definitions = new_definitions
        self.status = SessionStatus.THINKING
