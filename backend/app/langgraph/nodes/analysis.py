import time
from backend.app.langgraph.state import GraphState
from backend.app.core.logging import logger

async def analysis_node(state: GraphState) -> dict:
    """Analysis node: extracts business intelligence from collected search results."""
    logger.info("--- ANALYSIS NODE (MOCK) ---")
    start_time = time.time()
    
    # Simulate work
    time.sleep(0.5)
    
    metrics = state.get("execution_metrics", {})
    metrics["analyzing"] = round(time.time() - start_time, 2)
    
    # Mock analysed data
    analysed_data = {
        "overview": f"{state['company_name']} is an emerging leader in enterprise solutions.",
        "products": "Enterprise SaaS portal, AI assistant plug-ins, automated reporting services.",
        "customers": "Sales departments, enterprise operations groups, business intelligence units.",
        "signals": "Recently announced new funding round, partnership with major cloud provider.",
        "risks": "Fierce market competition, potential changes in AI regulation frameworks."
    }
    
    return {
        "analysed_data": analysed_data,
        "status": "analyzing",
        "execution_metrics": metrics
    }
