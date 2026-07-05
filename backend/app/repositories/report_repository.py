from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import uuid

from backend.app.models.models import Report
from backend.app.schemas.schemas import ReportCreate

class ReportRepository:
    @staticmethod
    async def create(db: AsyncSession, session_id: str, report_in: ReportCreate) -> Report:
        db_report = Report(
            id=str(uuid.uuid4()),
            session_id=session_id,
            markdown_content=report_in.markdown_content,
            json_content=report_in.json_content,
            confidence_score=report_in.confidence_score
        )
        db.add(db_report)
        await db.commit()
        await db.refresh(db_report)
        return db_report

    @staticmethod
    async def get_by_session_id(db: AsyncSession, session_id: str) -> Optional[Report]:
        query = select(Report).where(Report.session_id == session_id).order_by(Report.created_at.desc())
        result = await db.execute(query)
        return result.scalars().first()
