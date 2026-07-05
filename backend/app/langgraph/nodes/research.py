import time
from backend.app.langgraph.state import GraphState
from backend.app.core.logging import logger

async def research_node(state: GraphState) -> dict:
    """Research node: gathers web search results for the target company."""
    logger.info("--- RESEARCH NODE (MOCK) ---")
    start_time = time.time()
    
    # Simulate work
    time.sleep(0.5)
    
    metrics = state.get("execution_metrics", {})
    metrics["research"] = round(time.time() - start_time, 2)
    
    mock_results = [
        {
            "title": f"{state['company_name']} Official Website Overview",
            "url": f"https://www.{state['website']}",
            "published_date": "2026-01-01",
            "source_type": "web",
            "content": f"{state['company_name']} is a leading enterprise tech vendor specializing in SaaS platforms and AI integrations.",
            "relevance_score": 1.0
        }
    ]
    
    # In a real run, we accumulate results. Since it's a mock, we just set or append.
    current_results = state.get("search_results", []) or []
    current_results.extend(mock_results)
    
    return {
        "search_results": current_results,
        "status": "researching",
        "execution_metrics": metrics
    }
