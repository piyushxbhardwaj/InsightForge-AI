import time
from backend.app.langgraph.state import GraphState
from backend.app.services.llm_service import LLMService
from backend.app.prompts.planner_prompt import PLANNER_PROMPT_TEMPLATE
from backend.app.core.logging import logger

async def planner_node(state: GraphState) -> dict:
    """
    Planner Node:
    Uses the configured LLM to generate a targeted research search plan
    consisting of 3 to 5 precise search queries.
    """
    logger.info(f"--- STARTING PLANNER NODE for: {state['company_name']} ---")
    start_time = time.time()
    
    # Setup LLM service
    llm_service = LLMService()
    
    # Format the prompt template
    prompt = PLANNER_PROMPT_TEMPLATE.format(
        company_name=state["company_name"],
        website=state["website"],
        research_objective=state["research_objective"]
    )
    
    # Call the LLM
    response = await llm_service.call_llm(
        prompt=prompt,
        system_prompt="You are an expert sales intelligence planner. Output only the queries requested.",
        category="planner"
    )
    
    # Parse bullet points into a clean list of queries
    queries = []
    for line in response.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        
        # Clean standard markdown bullets
        if line.startswith("-") or line.startswith("*") or line.startswith("•"):
            line = line[1:].strip()
        # Clean numbered lists like "1. query"
        elif len(line) > 2 and line[0].isdigit():
            # Find first dot or paren and strip
            for idx, char in enumerate(line[:5]):
                if char in (".", ")"):
                    line = line[idx+1:].strip()
                    break
                    
        if line:
            queries.append(line)
            
    # Safeguard in case parsing fails completely: fall back to default queries
    if not queries:
        logger.warning("Failed to parse LLM search plan queries. Using fallback queries.")
        queries = [
            f"{state['company_name']} overview and products",
            f"{state['company_name']} business news and leadership",
            f"{state['company_name']} competitors and risks"
        ]
        
    execution_time = round(time.time() - start_time, 2)
    metrics = state.get("execution_metrics", {}) or {}
    metrics["planner"] = execution_time
    
    logger.info(f"Planner finished in {execution_time}s. Generated {len(queries)} queries.")
    
    return {
        "search_plan": queries,
        "status": "planning",
        "execution_metrics": metrics
    }
