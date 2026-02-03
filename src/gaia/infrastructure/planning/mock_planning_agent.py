from typing import List, Optional, Tuple

from gaia.application.planning.planning_agent import PlanningAgent
from gaia.domain.ai.tool import ToolCall
from gaia.domain.planning.plan import Objective, Plan, Strategy
from gaia.domain.planning.planning_session import PlanningSession

DEFAULT_MOCK_PLAN_JSON = {
    "overall_objective": "MOCK: Eliminate threat and secure resources.",
    "objectives": [
        {
            "type": "DefeatCharacter",
            "parameters": {
                "target_type_id": "1db032f1-62c5-4271-b752-e0b6a953f8aa",
                "target_quantity": 3,
            },
            "priority": 10,
        },
        {
            "type": "AcquireItem",
            "parameters": {
                "target_item_id": "58d36adf-70d7-4e47-91a4-10db1ee6727a",
                "target_quantity": 3,
            },
            "priority": 10,
        },
    ],
    "strategy": {
        "priority": "Aggressive",
        "engagement": "EngageAll",
        "retreat_condition": {"health_below": 0.2},
    },
    "thought": "This is a mock response.",
}


class MockPlanningAgent(PlanningAgent):
    async def think(
        self, session: PlanningSession
    ) -> Tuple[str, List[ToolCall], Optional[Plan]]:
        plan = Plan(
            overall_objective=DEFAULT_MOCK_PLAN_JSON["overall_objective"],
            objectives=[Objective(**o) for o in DEFAULT_MOCK_PLAN_JSON["objectives"]],
            strategy=Strategy(**DEFAULT_MOCK_PLAN_JSON["strategy"]),
            thought=DEFAULT_MOCK_PLAN_JSON["thought"],
        )

        return plan.thought, [], plan
