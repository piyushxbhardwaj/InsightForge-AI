# InsightForge AI - Sales & Business Intelligence Research Copilot

InsightForge AI is a production-grade, AI-powered research workstation designed for Sales and Business Intelligence teams. It automates pre-meeting company research by executing a multi-node **LangGraph** agent workflow, streaming live node transitions, compiling structured markdown/JSON reports, and providing a context-constrained, hallucination-free chatbot for follow-up questions.

---

## 🚀 Features

- **Multi-Node Agent Workflow (LangGraph)**: Executed across five specialized nodes:
  - **Planner**: Generates tailored search queries.
  - **Research**: Scrapes web documents via Tavily, with URL deduplication.
  - **Analysis**: Extracts products, customer profiles, signals, and competitors.
  - **Quality Check**: Scores coverage, confidence, and freshness, with conditional routing loop limits.
  - **Report Generator**: Synthesizes the final markdown and JSON report.
- **Server-Sent Events (SSE)**: Streams node execution transitions and timing metrics in real-time to the frontend.
- **Normalized SQLite Database**: NORMALIZED schema (`sessions`, `sources`, `reports`, `chat_messages`, `workflow_logs`).
- **Context-Aware Follow-up Chat**: A chatbot restricted strictly to report context, preventing hallucinations.
- **SQLite Cache Layer**: Checks recently completed sessions to offer instant loads and save API costs.
- **Observability Telemetry**: Tracks and prints precise performance timing cards on stdout.

---

## 🛠️ Technology Stack

### Frontend
- React 19, Vite, TypeScript, Tailwind CSS, Framer Motion, TanStack Query, Axios, React Markdown, Lucide Icons.

### Backend
- Python 3.12, FastAPI, LangGraph, LangChain, SQLAlchemy, Pydantic v2, Tavily, aiosqlite, Uvicorn.

---

## 📁 Repository Structure

```text
InsightForge-AI/
├── frontend/                 # React 19 SPA (Vite + TypeScript)
│   ├── src/
│   │   ├── components/       # UI Components (Sidebar, Form, Progress, Viewer, Chat)
│   │   ├── services/         # Axios API connection
│   │   ├── types/            # TypeScript definitions
│   │   └── App.tsx           # Main workspace orchestration
│   └── package.json
│
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/              # Route controllers (sessions, workflow, chat)
│   │   ├── config/           # BaseSettings config loader
│   │   ├── core/             # Logging initializer
│   │   ├── database/         # connection pool & init scripts
│   │   ├── models/           # SQLAlchemy model definitions
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Service layer (workflow, LLM, search, chat)
│   │   ├── prompts/          # Isolated prompt templates
│   │   ├── langgraph/        # Graph workflow definitions
│   │   │   ├── nodes/        # Individual node actions
│   │   │   └── graphs/       # Assembled StateGraph
│   │   └── main.py           # Backend server entrypoint
│   └── requirements.txt
│
└── docs/                     # Engineering design files
    ├── architecture.md
    ├── engineering-decisions.md
    └── product-improvements.md
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory:

```env
DATABASE_URL=sqlite+aiosqlite:///./insightforge.db
LOG_LEVEL=INFO
PORT=8000
HOST=0.0.0.0

# LLM Providers (Minimum one is required)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Search API
TAVILY_API_KEY=your_tavily_api_key_here
```

*Note: If no valid keys are supplied, the application automatically runs in **Mock mode**, generating mock responses to allow full evaluation.*

---

## 🏁 Installation & Startup

### Prerequisites
- Python 3.11+
- Node.js 18+

### Step 1: Run the Backend
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI development server:
   ```bash
   python -m app.main
   ```
   The backend will start on `http://localhost:8000`. The SQLite database will be initialized automatically.

### Step 2: Run the Frontend
1. Open a new terminal in the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Launch the Vite development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 📡 API Documentation

Access Swagger docs at `http://localhost:8000/docs`.

### Sessions
- `GET /api/sessions`: List all sessions.
- `POST /api/sessions`: Create session (supports cache checking).
- `GET /api/sessions/{id}`: Fetch detailed session (eager loaded).
- `GET /api/sessions/check-cache`: Lookup recently completed sessions.

### Workflow
- `POST /api/workflow/{id}`: Initialize graph execution.
- `GET /api/workflow/{id}/stream`: Stream real-time node transitions using SSE.

### Chat
- `GET /api/chat/{id}`: Load follow-up message history.
- `POST /api/chat/{id}`: Query report context.

---

## 🌍 Cloud Deployment Targets

- **Frontend**: Deploy to **Vercel** by wiring the `frontend/` folder. Configure CORS origins.
- **Backend**: Deploy to **Render** or **Railway**. Set build commands to install dependencies and run uvicorn.
- **Database**: The project uses SQLite. For cloud environments, swap to a hosted PostgreSQL instance by setting the `DATABASE_URL` env variable on Render/Railway.
