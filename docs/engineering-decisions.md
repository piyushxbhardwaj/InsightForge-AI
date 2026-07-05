# InsightForge AI - Engineering Decisions

---

## 1. Decision 1: Adopting LangGraph over Linear LangChain Chains

- **Rationale**: Company research is an iterative process. A quality assessment step can fail and demand more queries. Linear pipelines (like LangChain Sequentials) cannot branch or loop back without manual, spaghetti-like code handlers.
- **Alternatives Considered**: 
  1. *Linear Chain*: Simple to code but fails to handle quality check loops.
  2. *Custom Agent Executor Loop*: Hard to state-manage and log step-by-step progress.
- **Tradeoffs**: LangGraph has a steeper learning curve and adds dependencies. However, it provides a strongly typed shared state, standard checkpointing, and clean conditional routing paths out-of-the-box.

---

## 2. Decision 2: Storing Structured JSON Sections Alongside Markdown Reports

- **Rationale**: For follow-up chat queries, injecting the entire markdown report into the prompt consumes high token volumes. By storing a structured JSON copy in the `reports` table, the chat service can inject only the specific section relevant to the user query (or a lightweight JSON profile) to save API costs and improve response latencies.
- **Alternatives Considered**: 
  1. *Markdown Only*: Simple DB writing, but demands regex parsing of headers during chat context injection.
  2. *Direct Embeddings (Vector DB)*: Excellent for huge libraries, but overkill for single-session document analysis.
- **Tradeoffs**: Storing both duplicate formats increases SQLite storage footprint slightly, but optimizes runtime token counts and provides direct support for structured frontend card rendering.

---

## 3. Decision 3: SQLite Cache Layer

- **Rationale**: Tavily and LLM API calls are expensive and slow. Sales representatives often research the same major companies (e.g. Microsoft, Snowflake) repeatedly. Checking a local cache prior to running the graph saves cost and returns reports instantly (cache hit response under 100ms).
- **Alternatives Considered**:
  1. *Redis Cache*: High performance, but adds setup complexity and operational dependencies.
  2. *Memory Cache*: Simple dict cache, but disappears on server restarts.
- **Tradeoffs**: SQLite caching preserves cache records across restarts and requires zero configuration. The tradeoff is database file size, which we mitigate by adding a `CACHE_EXPIRATION_SECONDS` config (defaulting to 24 hours).

---

## 4. Plan for Two Additional Weeks

If given two additional weeks, the engineering roadmap would focus on:

### Week 1: Human-in-the-Loop (HITL) Checkpoint Interruption
- Configure LangGraph's native state memory checkpointers (`SqliteSaver`).
- Add a workflow interruption step after the Planner node. The backend halts execution and sends the generated queries to the frontend.
- The user can review, edit, add, or delete search queries before clicking "Resume", triggering the remaining nodes.

### Week 2: RAG Vector Search & PDF Export
- Set up an embedded vector database (e.g. ChromaDB or pgvector) inside the workspace to index the raw content of all scraped articles.
- The follow-up chat chatbot will query this database instead of just the report, allowing users to query deeper facts that did not make it into the final report.
- Integrate a pdf generation service (`WeasyPrint` or `ReportLab`) to export clean executive briefs.
