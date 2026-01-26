import json

from gaia.application.ai.dto import (
    ToolCallDto,
    ToolDefinitionDto,
    ToolOutputDto,
)
from gaia.domain.ai.tool import (
    ToolCall,
    ToolDefinition,
    ToolOutput,
)


class AIMapper:
    @staticmethod
    def to_tool_definition(dto: ToolDefinitionDto) -> ToolDefinition:
        return ToolDefinition(
            name=dto.name, description=dto.description, parameters=dto.parameters
        )

    @staticmethod
    def to_tool_output(dto: ToolOutputDto) -> ToolOutput:
        return ToolOutput(tool_call_id=dto.tool_call_id, output=dto.output)

    @staticmethod
    def to_tool_call_dto(tool_call: ToolCall) -> ToolCallDto:
        return ToolCallDto(
            id=tool_call.id,
            function_name=tool_call.function_name,
            arguments=json.dumps(tool_call.arguments),
        )
