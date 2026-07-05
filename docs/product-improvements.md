# InsightForge AI - Product Analysis and Improvements

---

## 1. Five Product Weaknesses (Product Critique)

1. **Static Report Content**: Once a research session finishes, the report is immutable. A user cannot instruct the planner to add a new section or refresh research on specific indicators without starting a new session.
2. **Missing Source Text Highlight**: When inspecting sources in the references tab, users can read the URL and snippet, but cannot see where in the generated report those facts were cited.
3. **No PDF/Word Export Options**: Exporting reports is restricted to copy-pasting markdown. Sales representatives need PDF summaries to send directly to executives before meetings.
4. **Basic Web Scraper**: The fallback search relies on HTML snippets which can fail to capture deep textual structures on complex, React-rendered corporate landing pages.
5. **No Collaborative Sharing**: Research logs are local to a single user's browser dashboard. Team sharing or collaborative meeting workspace channels are absent.

---

## 2. Top Three Improvements

1. **Interactive Document Customization (Add-on Node)**:
   Integrate a human-in-the-loop (HITL) step after the Quality Check node where users can view the research plan and suggest adding custom questions before compiling.
2. **Exportable PDF and PowerPoint Slides**:
   Implement a report exporter compiling the structured JSON into clean executive PDF pages or pitch slide templates.
3. **Interactive Citation Highlights**:
   Enrich the JSON report model to map citation numbers (e.g. `[1]`) to specific sources, allowing users to hover over claims and see the corresponding source url.

---

## 3. Personas

### Buyer Persona
- **Name**: Sarah Jenkins
- **Role**: VP of Sales Operations at a B2B SaaS startup (50-200 employees)
- **Pain Points**: Sales reps spend 30-45 minutes prepping for every meeting, which reduces active calling time. Preparation quality varies greatly across team members.
- **Goals**: Standardize pre-meeting company intelligence files, boost team calling velocity, and improve outreach conversion rates.

### User Persona
- **Name**: Piyush Bhardwaj
- **Role**: B2B Sales Development Representative (SDR)
- **Pain Points**: Needs to research 15 target prospects a day. Copying-pasting facts from blogs and news is exhausting. He frequently misses key signals like recent cloud migrations or funding changes.
- **Goals**: Instantly digest a company's product line, risks, and discovery questions before an intro call to establish immediate credibility.

---

## 4. Success Metrics

- **SDR Prep Efficiency**: Reduce pre-call company research time from an average of 35 minutes down to 3 minutes (90%+ time savings).
- **Outreach Response Rate**: Increase response rates on custom emails by 25% due to tailored discovery questions.
- **Meeting Hook Success**: Percentage of SDR calls where outreach strategy suggestions successfully hooked prospect attention.
- **Cache Reuse Rate**: Percentage of company searches resolved instantly via SQLite caches (saving external Tavily and LLM API costs).

---

## 5. Operational Risks

### Scaling Risks
- **Concurrency Limits**: sqlite database writing locks can present bottlenecks under heavy concurrent load. 
- **Mitigation**: Migrate to a PostgreSQL database on cloud setups.

### Reliability Risks
- **Web Scraping Blocks**: Sites protected by Cloudflare or recaptcha block simple scrapers.
- **Mitigation**: Route search requests through Tavily's proxy networks and integrate a premium scraper tool like Firecrawl.

### Cost Risks
- **LLM Token Volume**: Multi-node runs require multiple LLM calls, which can spike costs when searching large entities.
- **Mitigation**: Cache search findings and use lightweight models (Gemini 1.5 Flash) for planner and analysis nodes, reserving premium models (GPT-4o) only for report synthesis.

---

## 6. Proposed Feature Changes

### Feature to Remove
- **Generic Search Bar**: Instead of letting users enter completely arbitrary search terms, restrict form inputs strictly to **Company Name** and **Domain/Website URL**. This avoids LLM planning drift and focuses Tavily search scopes on relevant company domains.

### Feature to Add
- **Calendar Integration Hook**:
  Scan the user's Google/Outlook Calendar, identify upcoming external attendee email domains, and pre-run research graphs in the background so reports are ready in the dashboard before the meeting starts.
