import time
from backend.app.langgraph.state import GraphState
from backend.app.core.logging import logger

async def planner_node(state: GraphState) -> dict:
    """Planner node: generates a research search plan for the target company."""
    logger.info("--- PLANNER NODE (MOCK) ---")
    start_time = time.time()
    
    # Simulate work
    time.sleep(0.5)
    
    metrics = state.get("execution_metrics", {})
    metrics["planner"] = round(time.time() - start_time, 2)
    
    return {
        "search_plan": [
            f"{state['company_name']} overview business model",
            f"{state['company_name']} products services target customers",
            f"{state['company_name']} news competitors risks signals"
        ],
        "status": "planning",
        "execution_metrics": metrics
    }
