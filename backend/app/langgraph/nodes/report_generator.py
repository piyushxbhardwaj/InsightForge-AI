import time
from backend.app.langgraph.state import GraphState
from backend.app.core.logging import logger

async def report_generator_node(state: GraphState) -> dict:
    """Report Generator node: compiles the final structured markdown and JSON research report."""
    logger.info("--- REPORT GENERATOR NODE (MOCK) ---")
    start_time = time.time()
    
    # Simulate work
    time.sleep(0.5)
    
    metrics = state.get("execution_metrics", {})
    metrics["report_generation"] = round(time.time() - start_time, 2)
    
    company = state["company_name"]
    objective = state["research_objective"]
    
    report_markdown = f"""# Research Report: {company}

## Company Overview
{company} is a leading technology enterprise company.

## Products & Services
- Enterprise SaaS solutions
- AI assistant plug-ins

## Target Customers
- Corporate business groups
- Business intelligence teams

## Business Signals
- Cloud partner alignments
- Funding expansion activities

## Risks & Challenges
- Fast-changing regulations
- Technology market competition

## Suggested Discovery Questions
1. How does {company} manage compliance rules?
2. What are the key bottlenecks in current scaling models?

## Suggested Outreach Strategy
Present our enterprise scale-up integration templates as a solution to operational overhead.

## Unknowns
- Internal team expansion velocity.

## Sources
- {company} Official Website (https://www.{state['website']})
"""

    report_json = {
        "company_overview": f"{company} is a leading technology enterprise company.",
        "products_services": ["Enterprise SaaS solutions", "AI assistant plug-ins"],
        "target_customers": ["Corporate business groups", "Business intelligence teams"],
        "business_signals": ["Cloud partner alignments", "Funding expansion activities"],
        "risks_challenges": ["Fast-changing regulations", "Technology market competition"],
        "suggested_discovery_questions": [
            f"How does {company} manage compliance rules?",
            f"What are the key bottlenecks in current scaling models?"
        ],
        "suggested_outreach_strategy": "Present our enterprise scale-up integration templates as a solution to operational overhead.",
        "unknowns": ["Internal team expansion velocity."],
        "sources": [
            {
                "title": f"{company} Official Website",
                "url": f"https://www.{state['website']}"
            }
        ]
    }
    
    return {
        "report_markdown": report_markdown,
        "report_json": report_json,
        "status": "completed",
        "execution_metrics": metrics
    }
