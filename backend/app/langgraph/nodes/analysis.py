import time
import json
from backend.app.langgraph.state import GraphState
from backend.app.services.llm_service import LLMService
from backend.app.prompts.analysis_prompt import ANALYSIS_PROMPT_TEMPLATE
from backend.app.core.logging import logger

async def analysis_node(state: GraphState) -> dict:
    """
    Analysis Node:
    Takes search results and uses the LLM to extract structured business intelligence:
    overview, products_services, target_customers, business_signals, risks.
    """
    logger.info(f"--- STARTING ANALYSIS NODE for: {state['company_name']} ---")
    start_time = time.time()
    
    llm_service = LLMService()
    
    # 1. Compile search results into text representation
    search_results = state.get("search_results", []) or []
    if not search_results:
        logger.warning("No search results found in state. Creating analysis from objective details.")
        search_results_text = "No search findings collected."
    else:
        results_list = []
        for idx, res in enumerate(search_results):
            source_info = (
                f"Source [{idx+1}]: {res.get('title', 'Unknown')}\n"
                f"URL: {res.get('url', 'N/A')}\n"
                f"Content: {res.get('content', '')}\n"
            )
            results_list.append(source_info)
        search_results_text = "\n".join(results_list)

    # 2. Format the analysis prompt
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        company_name=state["company_name"],
        research_objective=state["research_objective"],
        search_results_text=search_results_text
    )
    
    # 3. Call LLM
    response = await llm_service.call_llm(
        prompt=prompt,
        system_prompt="You are a precise business intelligence parser. Respond only in raw JSON.",
        category="analysis"
    )
    
    # 4. Clean and parse JSON response
    response_text = response.strip()
    # Strip markdown wrapper if present
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    response_text = response_text.strip()
    
    try:
        analysed_data = json.loads(response_text)
        # Ensure all required keys exist
        required_keys = ["overview", "products_services", "target_customers", "business_signals", "risks"]
        for key in required_keys:
            if key not in analysed_data:
                analysed_data[key] = f"No {key.replace('_', ' ')} could be analyzed from sources."
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse analysis node JSON response: {e}. Raw response: {response}")
        # Graceful fallback: populate overview with raw response and empty others
        analysed_data = {
            "overview": f"Raw analysis output: {response}",
            "products_services": "Unable to parse from intelligence response.",
            "target_customers": "Unable to parse from intelligence response.",
            "business_signals": "Unable to parse from intelligence response.",
            "risks": "Unable to parse from intelligence response."
        }
        
    execution_time = round(time.time() - start_time, 2)
    metrics = state.get("execution_metrics", {}) or {}
    metrics["analyzing"] = execution_time
    
    logger.info(f"Analysis finished in {execution_time}s.")
    
    return {
        "analysed_data": analysed_data,
        "status": "analyzing",
        "execution_metrics": metrics
    }
