import time
from backend.app.langgraph.state import GraphState
from backend.app.core.logging import logger

async def quality_check_node(state: GraphState) -> dict:
    """Quality Check node: evaluates the completeness and confidence of research findings."""
    logger.info("--- QUALITY CHECK NODE (MOCK) ---")
    start_time = time.time()
    
    # Simulate work
    time.sleep(0.5)
    
    metrics = state.get("execution_metrics", {})
    metrics["quality_check"] = round(time.time() - start_time, 2)
    
    # We check if we have enough sources and details.
    # In mock, we pass it immediately.
    quality_assessment = {
        "coverage": "9/9 sections covered",
        "confidence": 0.95,
        "source_count": len(state.get("search_results", []) or []),
        "freshness_score": 0.9,
        "citation_quality": 1.0,
        "missing_sections": [],
        "overall_score": 0.93,
        "recommendation": "generate_report"
    }
    
    return {
        "quality_assessment": quality_assessment,
        "status": "quality_check",
        "execution_metrics": metrics
    }
