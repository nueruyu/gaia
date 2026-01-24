import json
from dataclasses import dataclass, replace

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import END, START, StateGraph

from gaia.application.dtos import PlanRequest
from gaia.application.interfaces.llm_service import LlmService
from gaia.domain.entities import Plan
from gaia.infrastructure.llm.prompts import PLAN_GENERATION_PROMPT


@dataclass(frozen=True)
class GraphState:
    request: PlanRequest
    formatted_prompt: str | None = None
    llm_output: str | None = None
    parsed_plan: Plan | None = None
    error: str | None = None


class LangChainLlmService(LlmService):
    def __init__(self, llm: BaseChatModel):
        self._llm = llm
        self._app = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(GraphState)
        workflow.add_node("format_prompt", self._format_prompt_node)
        workflow.add_node("call_llm", self._call_llm_node)
        workflow.add_node("parse_plan", self._parse_plan_node)
        workflow.add_edge(START, "format_prompt")
        workflow.add_edge("format_prompt", "call_llm")
        workflow.add_edge("call_llm", "parse_plan")
        workflow.add_edge("parse_plan", END)
        return workflow.compile()

    def _format_prompt_node(self, state: GraphState) -> GraphState:
        request = state.request
        prompt = PLAN_GENERATION_PROMPT.format(
            agent_character_type=request.context.agent_character_type,
            mission_objective=request.context.mission_objective,
            available_goals=json.dumps(
                [g.model_dump() for g in request.available_goals], indent=2
            ),
            character_types=json.dumps(
                [c.model_dump() for c in request.definitions.character_types], indent=2
            ),
            item_types=json.dumps(
                [i.model_dump() for i in request.definitions.item_types], indent=2
            ),
        )
        return replace(state, formatted_prompt=prompt)

    def _call_llm_node(self, state: GraphState) -> GraphState:
        if not state.formatted_prompt:
            return replace(state, error="Prompt was not formatted.")
        response = self._llm.invoke(state.formatted_prompt)
        return replace(state, llm_output=response.content)

    def _parse_plan_node(self, state: GraphState) -> GraphState:
        if state.llm_output is None:
            raise RuntimeError("llm_output is not set")
        parser = PydanticOutputParser(pydantic_object=Plan)
        try:
            parsed_plan = parser.parse(state.llm_output)
            return replace(state, parsed_plan=parsed_plan)
        except Exception as e:
            return replace(state, error=f"Failed to parse LLM output: {e}")

    def create_plan(self, request: PlanRequest) -> Plan:
        initial_state = GraphState(request=request)
        final_state_dict = self._app.invoke(initial_state)
        final_state = GraphState(**final_state_dict)
        if final_state.error:
            raise ValueError(final_state.error)
        if not final_state.parsed_plan:
            raise ValueError("Plan could not be created by the LLM.")
        return final_state.parsed_plan
