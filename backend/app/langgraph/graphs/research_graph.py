from langgraph.graph import StateGraph, START, END
from backend.app.langgraph.state import GraphState
from backend.app.langgraph.nodes.planner import planner_node
from backend.app.langgraph.nodes.research import research_node
from backend.app.langgraph.nodes.analysis import analysis_node
from backend.app.langgraph.nodes.quality_check import quality_check_node
from backend.app.langgraph.nodes.report_generator import report_generator_node
from backend.app.core.logging import logger

def quality_check_router(state: GraphState) -> str:
    """
    Evaluates the quality check outcome to decide whether to routing back 
    to the Research Node for more details, or advance to the Report Generator Node.
    """
    assessment = state.get("quality_assessment", {}) or {}
    confidence = assessment.get("confidence", 0.0)
    retry_count = state.get("retry_count", 0)
    
    logger.info(f"Routing evaluation - Confidence: {confidence}, Retry Count: {retry_count}")
    
    # If confidence is low and we have not exceeded the retry limit (e.g., 2), route back to research
    if confidence < 0.8 and retry_count < 2:
        logger.info("Quality check failed. Routing back to RESEARCH node.")
        return "research"
    else:
        logger.info("Quality check passed or max retries reached. Routing to REPORT_GENERATOR node.")
        return "report_generator"

# Construct the graph
workflow = StateGraph(GraphState)

# Register the nodes
workflow.add_node("planner", planner_node)
workflow.add_node("research", research_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("quality_check", quality_check_node)
workflow.add_node("report_generator", report_generator_node)

# Connect the nodes (flow definition)
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "research")
workflow.add_edge("research", "analysis")
workflow.add_edge("analysis", "quality_check")

# Configure the quality check conditional router
workflow.add_conditional_edges(
    "quality_check",
    quality_check_router,
    {
        "research": "research",
        "report_generator": "report_generator"
    }
)

# Connect report generator output to completion END
workflow.add_edge("report_generator", END)

# Compile graph
research_graph = workflow.compile()
