from typing import List

from gaia.domain.ai.message import AIMessage, Message
from gaia.domain.ai.tool import ToolDefinition
from gaia.infrastructure.llms.llm import Llm


class MockLlm(Llm):
    async def invoke(
        self, _messages: List[Message], _tool_definitions: List[ToolDefinition]
    ) -> AIMessage:
        dummy_plan_json = """
{
    "overall_objective": "MOCK: Eliminate threat and secure resources.",
    "objectives": [
        {
            "type": "DefeatCharacter",
            "parameters": {
                "character_type_id": "1db032f1-62c5-4271-b752-e0b6a953f8aa",
                "quantity": 1
            },
            "priority": 10
        },
        {
            "type": "AcquireItem",
            "parameters": {
                "item_id": "58d36adf-70d7-4e47-91a4-10db1ee6727a",
                "quantity": 1
            },
            "priority": 5
        }
    ],
    "strategy": {
        "priority": "Aggressive",
        "engagement": "EngageAll",
        "retreat_condition": {
            "health_below": 0.2
        }
    },
    "thought": "This is a mock response. The player is the highest threat."
}
"""
        return AIMessage(content=dummy_plan_json, tool_calls=[])
