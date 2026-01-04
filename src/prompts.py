from langchain_core.prompts import ChatPromptTemplate

system_prompt_template = """
You are an expert AI game agent commander. Your role is to create a strategic plan for an agent in a game based on the current context and available information.

Your output MUST be a single, valid JSON object that strictly adheres to the provided `Plan` schema.
Do not include any other text, explanations, or markdown formatting around the JSON object.

The plan should consist of:
1.  `overall_objective`: A brief, high-level summary of what the plan aims to achieve.
2.  `objectives`: A list of specific, prioritized goals to accomplish.
3.  `strategy`: The general behavior and rules of engagement the agent should follow.
4.  `thought`: Your reasoning and strategic thinking process for creating this plan.

Analyze the agent's context, mission, and the available static data to make informed decisions. The plan should be logical, coherent, and effective for the given situation.
"""

human_prompt_template = """
Here is the current situation report:

**Agent Context:**
- Agent's Character Type: {agent_character_type}
- Current Mission: {mission_objective}

**Available Goals (What the agent can do):**
```json
{available_goals}
```

**Static Definitions (Game World Knowledge):**
- Character Types:
```json
{character_types}
```

- Item Types:
```json
{item_types}
```

Based on all the information above, generate the best strategic plan for the agent.
Remember to output only the JSON object for the plan.
"""

PLAN_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt_template),
        ("human", human_prompt_template),
    ]
)
