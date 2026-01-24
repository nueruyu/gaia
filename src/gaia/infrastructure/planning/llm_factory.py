from gaia.config import Settings
from gaia.infrastructure.langchain.chat_models import create_gemini
from gaia.infrastructure.llms.langchain_llm import LangChainLlm
from gaia.infrastructure.llms.llm import Llm
from gaia.infrastructure.llms.mock_llm import MockLlm

DEFAULT_MOCK_PLAN = """
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


def create_planning_llm(settings: Settings) -> Llm:
    if settings.LLM_MODE == "MOCK":
        return MockLlm(content=DEFAULT_MOCK_PLAN)
    elif settings.LLM_MODE == "GEMINI":
        return LangChainLlm(model=create_gemini())
    else:
        raise ValueError(f"Unknown LLM_MODE: {settings.LLM_MODE}")
