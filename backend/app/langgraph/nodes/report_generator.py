import time
import re
from backend.app.langgraph.state import GraphState
from backend.app.services.llm_service import LLMService
from backend.app.prompts.report_prompt import REPORT_PROMPT_TEMPLATE
from backend.app.core.logging import logger

def parse_markdown_to_json(md: str) -> dict:
    """
    Parses compiled markdown report sections into structured JSON matching the database schema.
    """
    sections = {
        "company_overview": "",
        "products_services": "",
        "target_customers": "",
        "business_signals": "",
        "risks_challenges": "",
        "suggested_discovery_questions": "",
        "suggested_outreach_strategy": "",
        "unknowns": "",
        "sources": []
    }
    
    # Split the markdown document by secondary headers '## '
    parts = re.split(r'^##\s+', md, flags=re.MULTILINE)
    
    for part in parts:
        lines = part.strip().split("\n")
        if not lines or len(lines) < 2:
            continue
            
        header = lines[0].strip().lower()
        content = "\n".join(lines[1:]).strip()
        
        if "overview" in header:
            sections["company_overview"] = content
        elif "product" in header:
            sections["products_services"] = content
        elif "customer" in header:
            sections["target_customers"] = content
        elif "signal" in header:
            sections["business_signals"] = content
        elif "risk" in header:
            sections["risks_challenges"] = content
        elif "question" in header:
            sections["suggested_discovery_questions"] = content
        elif "outreach" in header:
            sections["suggested_outreach_strategy"] = content
        elif "unknown" in header:
            sections["unknowns"] = content
        elif "source" in header:
            # Parse links of format: - [Title](URL)
            source_list = []
            links = re.findall(r'-\s+\[(.*?)\]\((.*?)\)', content)
            for title, url in links:
                source_list.append({"title": title, "url": url})
            sections["sources"] = source_list
            
    return sections

async def report_generator_node(state: GraphState) -> dict:
    """
    Report Generator Node:
    Takes analysed data and sources from the state, runs the report generation prompt,
    saves the markdown report, and parses it into JSON report sections.
    """
    logger.info(f"--- STARTING REPORT GENERATOR NODE for: {state['company_name']} ---")
    start_time = time.time()
    
    llm_service = LLMService()
    
    # 1. Compile analysed data into text
    analysed_data = state.get("analysed_data", {}) or {}
    analysed_data_list = []
    for k, v in analysed_data.items():
        analysed_data_list.append(f"[{k.upper()}]:\n{v}\n")
    analysed_data_text = "\n".join(analysed_data_list)
    
    # 2. Compile sources list into text
    search_results = state.get("search_results", []) or []
    sources_list = []
    for idx, res in enumerate(search_results):
        sources_list.append(f"- [{res.get('title', 'Source')}]({res.get('url', '')})")
    sources_text = "\n".join(sources_list)
    
    # 3. Format prompt
    prompt = REPORT_PROMPT_TEMPLATE.format(
        company_name=state["company_name"],
        research_objective=state["research_objective"],
        analysed_data_text=analysed_data_text,
        sources_text=sources_text
    )
    
    # 4. Invoke LLM
    report_markdown = await llm_service.call_llm(
        prompt=prompt,
        system_prompt="You are a professional research report compiler. Return only the markdown document.",
        category="report_generator"
    )
    
    # Ensure markdown starts cleanly without trailing spacing
    report_markdown = report_markdown.strip()
    
    # 5. Parse markdown report into structured JSON sections
    report_json = parse_markdown_to_json(report_markdown)
    
    # Extract confidence score from quality check if available
    quality_assessment = state.get("quality_assessment", {}) or {}
    confidence = quality_assessment.get("confidence", 0.85)

    execution_time = round(time.time() - start_time, 2)
    metrics = state.get("execution_metrics", {}) or {}
    metrics["report_generation"] = execution_time
    
    logger.info(f"Report Generation finished in {execution_time}s.")
    
    return {
        "report_markdown": report_markdown,
        "report_json": report_json,
        "status": "completed",
        "execution_metrics": metrics
    }
