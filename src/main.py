from fastapi import FastAPI, HTTPException
from src.schemas import PlanRequest, Plan
from src.agent import create_plan

app = FastAPI(
    title="Game AI Agent Server",
    description="An API server to generate strategic plans for game AI agents using LangGraph.",
    version="1.0.0",
)


@app.post("/request_plan", response_model=Plan)
async def request_plan_endpoint(request: PlanRequest):
    """
    Receives game state and context, then returns a strategic plan for an AI agent.
    """
    try:
        plan = create_plan(request)
        return plan
    except ValueError as e:
        raise HTTPException(
            status_code=500, detail=f"Agent failed to create a plan: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    A simple health check endpoint.
    """
    return {"status": "ok"}
