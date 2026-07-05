from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.app.core.logging import setup_logging
from backend.app.config.config import settings
from backend.app.database.init_db import init_db

# Initialize logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    await init_db()
    yield
    # Shutdown actions (none needed currently)

app = FastAPI(
    title="InsightForge AI API",
    description="Production-Grade AI Research Copilot API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration for Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to monitor API status."""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "app": "InsightForge AI API",
        "database": "connected"  # We'll hook this up to DB later
    }

if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
