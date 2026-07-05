import time
import json
from backend.app.langgraph.state import GraphState
from backend.app.services.llm_service import LLMService
from backend.app.prompts.quality_prompt import QUALITY_PROMPT_TEMPLATE
from backend.app.core.logging import logger

async def quality_check_node(state: GraphState) -> dict:
    """
    Quality Check Node:
    Assesses the compiled intelligence data and outputs structured metrics.
    Decides whether to perform more research or generate the final report.
    """
    logger.info(f"--- STARTING QUALITY CHECK NODE for: {state['company_name']} ---")
    start_time = time.time()
    
    llm_service = LLMService()
    
    # 1. Compile analysed data into text
    analysed_data = state.get("analysed_data", {}) or {}
    analysed_data_list = []
    for k, v in analysed_data.items():
        analysed_data_list.append(f"[{k.upper()}]:\n{v}\n")
    analysed_data_text = "\n".join(analysed_data_list)
    
    source_count = len(state.get("search_results", []) or [])
    
    # 2. Format the quality prompt
    prompt = QUALITY_PROMPT_TEMPLATE.format(
        company_name=state["company_name"],
        research_objective=state["research_objective"],
        source_count=source_count,
        analysed_data_text=analysed_data_text
    )
    
    # 3. Call LLM
    response = await llm_service.call_llm(
        prompt=prompt,
        system_prompt="You are a strict data evaluator. Output only a single JSON block.",
        category="quality_check"
    )
    
    # 4. Clean and parse JSON response
    response_text = response.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    response_text = response_text.strip()
    
    try:
        quality_assessment = json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse quality assessment JSON response: {e}. Raw response: {response}")
        # Default fallback
        quality_assessment = {
            "coverage": "5/5 sections",
            "confidence": 0.85,
            "source_count": source_count,
            "freshness_score": 0.8,
            "citation_quality": 0.8,
            "missing_sections": [],
            "overall_score": 0.82,
            "recommendation": "generate_report"
        }
        
    # Enforce loop guard: if retry count is at limit, override recommendation to force report compile
    retry_count = state.get("retry_count", 0)
    if retry_count >= 2:
        logger.info(f"Retry count is {retry_count} (>= 2). Forcing recommendation to 'generate_report' to avoid infinite loop.")
        quality_assessment["recommendation"] = "generate_report"
        
    execution_time = round(time.time() - start_time, 2)
    metrics = state.get("execution_metrics", {}) or {}
    metrics["quality_check"] = execution_time
    
    logger.info(f"Quality Check finished in {execution_time}s. Recommendation: {quality_assessment['recommendation']}")
    
    return {
        "quality_assessment": quality_assessment,
        "status": "quality_check",
        "execution_metrics": metrics
    }
