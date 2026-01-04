from dataclasses import dataclass, replace
import json
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, START, END

from gaia.application.interfaces.llm_service import LlmService
from gaia.application.dtos import PlanRequest
from gaia.domain.entities import Plan
from gaia.infrastructure.llm.prompts import PLAN_GENERATION_PROMPT

# This would be configured with your actual LLM provider, e.g., OpenAI, Anthropic, etc.
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4o", temperature=0)


@dataclass(frozen=True)
class GraphState:
    request: PlanRequest
    formatted_prompt: str | None = None
    llm_output: str | None = None
    parsed_plan: Plan | None = None
    error: str | None = None


def format_prompt_node(state: GraphState) -> GraphState:
    request = state.request
    context = request.context
    definitions = request.definitions
    prompt = PLAN_GENERATION_PROMPT.format(
        agent_character_type=context.agent_character_type,
        mission_objective=context.mission_objective,
        available_goals=json.dumps(
            [g.model_dump() for g in request.available_goals], indent=2
        ),
        character_types=json.dumps(
            [c.model_dump() for c in definitions.character_types], indent=2
        ),
        item_types=json.dumps(
            [i.model_dump() for i in definitions.item_types], indent=2
        ),
    )
    return replace(state, formatted_prompt=prompt)


def call_llm_node(state: GraphState) -> GraphState:
    # Dummy response for testing without a live LLM
    dummy_plan_json = """
    {
        "overall_objective": "Eliminate the primary threat and secure resources.",
        "objectives": [
            { "type": "DefeatCharacterType", "parameters": { "characterTypeId": "player" }, "priority": 10 },
            { "type": "CollectItem", "parameters": { "itemId": "item-guid-potion" }, "priority": 5 }
        ],
        "strategy": {
            "priority": "Aggressive",
            "engagement": "EngageAll",
            "retreat_condition": { "healthBelow": 0.2 }
        },
        "thought": "The player is the highest threat and must be neutralized first. Securing health potions is a secondary objective to sustain the assault."
    }
    """
    return replace(state, llm_output=dummy_plan_json)


def parse_plan_node(state: GraphState) -> GraphState:
    if state.llm_output is None:
        raise RuntimeError("llm_output is not set")
    parser = PydanticOutputParser(pydantic_object=Plan)
    try:
        parsed_plan = parser.parse(state.llm_output)
        return replace(state, parsed_plan=parsed_plan)
    except Exception as e:
        return replace(state, error=f"Failed to parse LLM output: {e}")


class LangChainLlmService(LlmService):
    def __init__(self):
        workflow = StateGraph(GraphState)
        workflow.add_node("format_prompt", format_prompt_node)
        workflow.add_node("call_llm", call_llm_node)
        workflow.add_node("parse_plan", parse_plan_node)
        workflow.add_edge(START, "format_prompt")
        workflow.add_edge("format_prompt", "call_llm")
        workflow.add_edge("call_llm", "parse_plan")
        workflow.add_edge("parse_plan", END)
        self._app = workflow.compile()

    def create_plan(self, request: PlanRequest) -> Plan:
        initial_state = GraphState(request=request)
        final_state_dict = self._app.invoke(initial_state)

        # langgraph returns a dict, so we convert it back to our state object
        final_state = GraphState(**final_state_dict)

        if final_state.error:
            raise ValueError(final_state.error)
        if not final_state.parsed_plan:
            raise ValueError("Plan could not be created.")

        return final_state.parsed_plan
