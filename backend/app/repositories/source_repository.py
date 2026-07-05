from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from backend.app.models.models import Source
from backend.app.schemas.schemas import SourceCreate

class SourceRepository:
    @staticmethod
    async def create(db: AsyncSession, session_id: str, source_in: SourceCreate) -> Source:
        db_source = Source(
            id=str(uuid.uuid4()),
            session_id=session_id,
            title=source_in.title,
            url=source_in.url,
            published_date=source_in.published_date,
            source_type=source_in.source_type,
            content=source_in.content,
            relevance_score=source_in.relevance_score
        )
        db.add(db_source)
        await db.commit()
        await db.refresh(db_source)
        return db_source

    @staticmethod
    async def get_by_session_id(db: AsyncSession, session_id: str) -> List[Source]:
        query = select(Source).where(Source.session_id == session_id).order_by(Source.relevance_score.desc())
        result = await db.execute(query)
        return list(result.scalars().all())
