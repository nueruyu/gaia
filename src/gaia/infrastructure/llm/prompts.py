import json

from langchain_core.prompts import ChatPromptTemplate

from gaia.domain.entities import Plan

plan_schema = Plan.model_json_schema()
plan_schema_str = json.dumps(plan_schema, indent=2)
escaped_plan_schema_str = plan_schema_str.replace("{", "{{").replace("}", "}}")

system_prompt_template = f"""
You are an expert AI game agent commander. Your role is to create a strategic plan for an agent in a game based on the current context and available information.

Your output MUST be a single, valid JSON object that strictly adheres to the following JSON Schema.
Do not include any other text, explanations, or markdown formatting around the JSON object.

**JSON Schema:**
```json
{escaped_plan_schema_str}
```
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
