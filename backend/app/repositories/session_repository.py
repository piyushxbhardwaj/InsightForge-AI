from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from backend.app.models.models import Session
from backend.app.schemas.schemas import SessionCreate
from backend.app.config.config import settings

class SessionRepository:
    @staticmethod
    async def create(db: AsyncSession, session_in: SessionCreate) -> Session:
        db_session = Session(
            id=str(uuid.uuid4()),
            company_name=session_in.company_name,
            website=session_in.website,
            research_objective=session_in.research_objective,
            status="pending"
        )
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        return db_session

    @staticmethod
    async def get_by_id(db: AsyncSession, session_id: str) -> Optional[Session]:
        query = select(Session).where(Session.id == session_id)
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Session]:
        query = select(Session).order_by(Session.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_status(db: AsyncSession, session_id: str, status: str) -> Optional[Session]:
        query = select(Session).where(Session.id == session_id)
        result = await db.execute(query)
        db_session = result.scalars().first()
        if db_session:
            db_session.status = status
            db_session.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(db_session)
        return db_session

    @staticmethod
    async def get_cached_session(db: AsyncSession, company_name: str) -> Optional[Session]:
        """
        Check if a completed research session for this company exists 
        within the expiration window (e.g., 24 hours).
        """
        expiration_limit = datetime.utcnow() - timedelta(seconds=settings.CACHE_EXPIRATION_SECONDS)
        query = (
            select(Session)
            .where(
                Session.company_name.ilike(company_name),
                Session.status == "completed",
                Session.created_at >= expiration_limit
            )
            .order_by(Session.created_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        return result.scalars().first()
