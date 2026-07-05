ANALYSIS_PROMPT_TEMPLATE = """You are a Senior Business Intelligence and Sales Analyst.
Your task is to synthesize the following web research findings for {company_name}.
Research Objective: {research_objective}

Search Findings:
{search_results_text}

Analyze the findings and extract insights into these exact areas:
1. Overview: A concise description of the company, its age, stage, and primary mission.
2. Products & Services: Details of what they build or sell, including key features and unique selling propositions.
3. Target Customers: Customer personas, industries, company sizes, or departments they target.
4. Business Signals: Recent developments like hiring acceleration, partnerships, reviews, or funding rounds.
5. Risks: Top threats like competitors, market constraints, compliance blocks, or high dependency elements.

Format your output as a raw, single JSON object containing these keys:
- "overview"
- "products_services"
- "target_customers"
- "business_signals"
- "risks"

Ensure your return is ONLY a valid JSON string. Do not include markdown code block formatting (like ```json), conversational text, or explanations.
"""
