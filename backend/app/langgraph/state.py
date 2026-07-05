from typing import TypedDict, List, Dict, Any

class GraphState(TypedDict):
    """
    Strongly typed shared state object representing the data flow 
    across all nodes in the InsightForge AI research LangGraph workflow.
    """
    company_name: str
    website: str
    research_objective: str
    search_plan: List[str]
    search_results: List[Dict[str, Any]]
    analysed_data: Dict[str, Any]
    quality_assessment: Dict[str, Any]
    report_markdown: str
    report_json: Dict[str, Any]
    status: str
    retry_count: int
    execution_metrics: Dict[str, float] # Maps node name to runtime in seconds
    errors: List[str]
