from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from backend.app.config.config import settings

# Create async engine for SQLite (using aiosqlite)
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=False,
    connect_args={"check_same_thread": False} # Required for SQLite async thread-safety
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()

async def get_db():
    """Dependency for providing database sessions in FastAPI route endpoints."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
