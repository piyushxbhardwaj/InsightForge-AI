# InsightForge AI - Sales & Business Intelligence Research Copilot

🤖 **Production-Grade AI Research Copilot powered by LangGraph, FastAPI, and React.**

---

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-emerald.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.0-blue.svg?style=flat-square&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1-indigo.svg?style=flat-square)](https://github.com/langchain-ai/langgraph)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## 💡 Why This Project?

Sales operations and business development representatives often spend significant time manually researching prospect companies before an introductory meeting. This manual pipeline is slow, inconsistent, and takes away from active calling time.

**InsightForge AI** automates this process end-to-end. By leveraging a **production-grade multi-agent LangGraph workflow**, the application scrapes the web, extracts core products, maps target buyer personas, scores data confidence, generates context-constrained outreach questions, and hosts a follow-up chat, streamlining preparation into a matter of seconds.

---

## 📖 Table of Contents
1. [Architecture](#-architecture)
2. [Project Walkthrough](#-project-walkthrough)
3. [Environment Configuration](#-environment-configuration)
4. [Installation & Startup](#-installation--startup)
5. [API Documentation](#-api-documentation)
6. [Cloud Deployment](#-cloud-deployment)
7. [Future Improvements](#-future-improvements)
8. [License](#-license)

---

## 🏗️ Architecture

InsightForge AI implements a clean, layered service-oriented architecture, applying SOLID principles and dependency inversion (FastAPI Controllers → Service Layers → Repositories → SQLite).

### System Topology

```text
       ┌────────────────────────────────────────────────────────┐
       │                     React Frontend                     │
       │    (Dashboard, SSE Stepper, Report Viewer, Chat UI)    │
       └───────────────┬──────────────────────────▲─────────────┘
                       │                          │
                       │ HTTP API                 │ Server-Sent Events
                       │ Requests                 │ (SSE Stream)
                       ▼                          │
       ┌──────────────────────────────────────────┴─────────────┐
       │                 FastAPI Backend Router                 │
       │    (/api/sessions, /api/workflow, /api/chat, /health)  │
       └───────────────┬────────────────────────────────────────┘
                       │
                       │ invokes orchestration
                       ▼
       ┌────────────────────────────────────────────────────────┐
       │                     Service Layer                      │
       │  (WorkflowService, LLMService, SearchService, Chat)    │
       └───────────────┬──────────────────────────┬─────────────┘
                       │                          │
                       │ executes queries         │ drives state
                       ▼                          ▼
       ┌───────────────────────────────┐  ┌─────────────────────┐
       │       Repository Layer        │  │      LangGraph      │
       │  (SessionRepo, SourceRepo,    │  │   Workflow Graph    │
       │   ReportRepo, ChatRepo, Log)  │  │ (Planner -> Research│
       └───────────────┬───────────────┘  │  -> Analysis -> QC  │
                       │                  │  -> Report)         │
                       ▼                  └─────────────────────┘
       ┌───────────────────────────────┐
       │     SQLite Database file      │
       │  (Normalized SQL tables)      │
       └───────────────────────────────┘
```

### AI Workflow Node Orchestration (LangGraph)

The graph executes with self-healing routing:
```text
           [START]
              │
              ▼
         ┌─────────┐
         │ Planner │ ──> Generates 3-5 targeted queries
         └─────────┘
              │
              ▼
        ┌──────────┐
   ┌──> │ Research │ ──> Scrapes web URLs & dedupes sources
   │    └──────────┘
   │          │
   │          ▼
   │    ┌──────────┐
   │    │ Analysis │ ──> Extracts overview, products, and risks
   │    └──────────┘
   │          │
   │          ▼
   │  ┌──────────────┐
   │  │ Quality Check│ ──> Verifies completeness & freshness
   │  └──────────────┘
   │          │
   │          ▼
   │      [Decision] 
   └───  Confidence < 80%? (Max 2 retries)
              │ No / Max Reached
              ▼
     ┌──────────────────┐
     │ Report Generator │ ──> Compiles Markdown & JSON maps
     └──────────────────┘
              │
              ▼
            [END]
```

---

## 📸 Project Walkthrough

### 1. The Research Dashboard
*Start a new session with form validation and instant SQLite cache hit warning prompts.*

![Dashboard Screenshot Placeholder](https://via.placeholder.com/800x450.png?text=Dashboard+Interactive+Form+and+Cache+Hit+UI)

### 2. Real-Time Workflow Stepper
*Watch LangGraph nodes transition live using FastAPI Server-Sent Events (SSE).*

![Workflow Progress Screenshot Placeholder](https://via.placeholder.com/800x450.png?text=SSE+LangGraph+Live+Node+Stepper+Timeline)

### 3. Report Viewer & Follow-Up Chat
*Analyze company cards alongside a hallucination-restricted sales copilot chatbot.*

![Report and Chat Workspace Screenshot Placeholder](https://via.placeholder.com/800x450.png?text=Side-by-Side+Structured+Report+Viewer+and+Restricted+Chat)

---

## ⚙️ Environment Configuration

Configure a `.env` file in the root workspace directory:

```env
DATABASE_URL=sqlite+aiosqlite:///./insightforge.db
LOG_LEVEL=INFO
PORT=8000
HOST=0.0.0.0

# LLM Providers (At least one is required)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Search API
TAVILY_API_KEY=your_tavily_api_key_here
```

*Note: If no valid keys are supplied, the application automatically triggers **Mock mode**, generating mock responses to allow full system evaluation.*

---

## 🏁 Installation & Startup

### Step 1: Run the Backend
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create, activate a virtual environment, and install libraries:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   ```
3. Run the backend entrypoint:
   ```bash
   python -m app.main
   ```

### Step 2: Run the Frontend
1. Open a new terminal in the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install npm packages and run:
   ```bash
   npm install
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 📡 API Documentation

Access Swagger docs at `http://localhost:8000/docs`.

- `POST /api/sessions`: Create session (supports cache checking).
- `GET /api/sessions/{id}`: Fetch detailed session (eager loaded).
- `GET /api/workflow/{id}/stream`: Stream real-time node transitions using SSE.
- `POST /api/chat/{id}`: Query report context.

---

## 🌍 Cloud Deployment

- **Frontend**: Deploy to **Vercel** by wiring the `frontend/` folder. Configure CORS origins.
- **Backend**: Deploy to **Render** or **Railway**. Set uvicorn start scripts.
- **Database**: Swap to a hosted **PostgreSQL** instance simply by setting the `DATABASE_URL` env variable on Render/Railway.

---

## 🔮 Future Improvements

- **Redis Caching**: Transition SQLite database cache to memory-based Redis caches.
- **Calendar Sync Hooks**: Autodetect calendar events to pre-research meeting domains.
- **HITL Checkpoints**: Interruption steps allowing users to edit queries before scraping.
- **PDF/PowerPoint Exporters**: Instant slides compilation.

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more details.
