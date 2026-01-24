from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from gaia.domain.ai.values import (
    AIMessage,
    HumanMessage,
    Message,
    ToolCall,
    ToolDefinition,
    ToolMessage,
    ToolOutput,
)
from gaia.domain.planning.entities import Plan


class DomainError(Exception):
    pass


class SessionStatus(str, Enum):
    THINKING = "Thinking"
    WAITING_FOR_TOOL = "WaitingForTool"
    COMPLETED = "Completed"


@dataclass
class PlanningSession:
    session_id: str
    history: List[Message]
    status: SessionStatus
    tool_definitions: List[ToolDefinition]
    generated_plan: Optional[Plan] = None

    @classmethod
    def create(
        cls, instruction: str, tool_definitions: List[ToolDefinition]
    ) -> "PlanningSession":
        return cls(
            session_id=str(uuid4()),
            history=[HumanMessage(content=instruction)],
            status=SessionStatus.THINKING,
            tool_definitions=tool_definitions,
        )

    def add_ai_response(
        self, content: str, tool_calls: List[ToolCall], parsed_plan: Optional[Plan]
    ):
        if self.status != SessionStatus.THINKING:
            raise DomainError(f"Status mismatch: Expected THINKING, got {self.status}")

        self.history.append(AIMessage(content=content, tool_calls=tool_calls))

        if parsed_plan:
            self.generated_plan = parsed_plan
            self.status = SessionStatus.COMPLETED
        elif tool_calls:
            self.status = SessionStatus.WAITING_FOR_TOOL
        else:
            raise DomainError(
                "LLM response must contain either tool calls or a valid plan JSON."
            )

    def add_tool_outputs(
        self, outputs: List[ToolOutput], new_definitions: List[ToolDefinition]
    ):
        if self.status != SessionStatus.WAITING_FOR_TOOL:
            raise DomainError("Session is not waiting for tool outputs.")

        last_msg = self.history[-1]
        if not isinstance(last_msg, AIMessage) or not last_msg.tool_calls:
            raise DomainError("No active tool calls found in history.")

        requested_ids = {tc.id for tc in last_msg.tool_calls}
        for output in outputs:
            if output.tool_call_id not in requested_ids:
                raise DomainError(f"Unexpected tool output id: {output.tool_call_id}")

            self.history.append(
                ToolMessage(tool_call_id=output.tool_call_id, content=output.output)
            )

        self.tool_definitions = new_definitions
        self.status = SessionStatus.THINKING
