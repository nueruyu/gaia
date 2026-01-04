from dataclasses import dataclass, replace
import json
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, START, END

from src.schemas import PlanRequest, Plan
from src.prompts import PLAN_GENERATION_PROMPT

# This would be configured with your actual LLM provider, e.g., OpenAI, Anthropic, etc.
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4o", temperature=0)


@dataclass(frozen=True)
class GraphState:
    """
    Defines the state passed between nodes in the graph.
    """

    request: PlanRequest
    formatted_prompt: str | None = None
    llm_output: str | None = None
    parsed_plan: Plan | None = None
    error: str | None = None


def format_prompt_node(state: GraphState) -> GraphState:
    """
    Formats the input for the LLM based on the request data.
    """
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
    """
    Calls the LLM to generate a plan.
    NOTE: This is a dummy implementation for now.
    """
    # In a real implementation, you would call the LLM like this:
    # prompt = state["formatted_prompt"]
    # response = llm.invoke(prompt)
    # llm_output = response.content

    # Dummy response for testing without a live LLM
    dummy_plan_json = """
    {
        "overall_objective": "Eliminate the primary threat and secure resources.",
        "objectives": [
            {
                "type": "DefeatCharacterType",
                "parameters": { "characterTypeId": "player" },
                "priority": 10
            },
            {
                "type": "CollectItem",
                "parameters": { "itemId": "item-guid-potion" },
                "priority": 5
            }
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
    """
    Parses the LLM's JSON output into a Pydantic model.
    """
    if state.llm_output is None:
        raise RuntimeError("llm_output is not set")

    parser = PydanticOutputParser(pydantic_object=Plan)
    try:
        parsed_plan = parser.parse(state.llm_output)
        return replace(state, parsed_plan=parsed_plan)
    except Exception as e:
        return replace(state, error=f"Failed to parse LLM output: {e}")


# Build the graph
workflow = StateGraph(GraphState)
workflow.add_node("format_prompt", format_prompt_node)
workflow.add_node("call_llm", call_llm_node)
workflow.add_node("parse_plan", parse_plan_node)

workflow.add_edge(START, "format_prompt")
workflow.add_edge("format_prompt", "call_llm")
workflow.add_edge("call_llm", "parse_plan")
workflow.add_edge("parse_plan", END)

# Compile the graph into a runnable app
app = workflow.compile()


def create_plan(request: PlanRequest) -> Plan:
    """
    Entry point function to run the agent graph and create a plan.
    """
    initial_state = GraphState(request=request)
    final_state = app.invoke(initial_state)

    if final_state.get("error"):
        raise ValueError(final_state["error"])

    return final_state["parsed_plan"]
