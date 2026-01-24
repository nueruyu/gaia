from typing import Any, Iterator, List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class MockChatModel(BaseChatModel):
    """A mock chat model that returns a predefined JSON response."""

    def _generate(self, messages: List[BaseMessage], **kwargs: Any) -> ChatResult:
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
        response_message = AIMessage(content=dummy_plan_json)
        generation = ChatGeneration(message=response_message)
        return ChatResult(generations=[generation])

    def _stream(
        self, messages: List[BaseMessage], **kwargs: Any
    ) -> Iterator[BaseMessage]:
        yield AIMessage(content="")

    @property
    def _llm_type(self) -> str:
        return "mock-chat-model"
