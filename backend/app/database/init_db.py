from backend.app.database.connection import engine, Base
from backend.app.models.models import Session, Source, Report, ChatMessage, WorkflowLog
from backend.app.core.logging import logger

async def init_db():
    """Create database tables if they do not exist."""
    logger.info("Initializing SQLite database tables...")
    try:
        async with engine.begin() as conn:
            # Drop all (for reset if needed, but here we just create if not exists)
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise e
