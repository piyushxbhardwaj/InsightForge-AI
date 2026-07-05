from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid

from backend.app.models.models import WorkflowLog
from backend.app.schemas.schemas import WorkflowLogCreate

class WorkflowLogRepository:
    @staticmethod
    async def create(db: AsyncSession, session_id: str, log_in: WorkflowLogCreate) -> WorkflowLog:
        db_log = WorkflowLog(
            id=str(uuid.uuid4()),
            session_id=session_id,
            node_name=log_in.node_name,
            status=log_in.status,
            execution_time_seconds=log_in.execution_time_seconds,
            checkpoint_data=log_in.checkpoint_data,
            message=log_in.message
        )
        db.add(db_log)
        await db.commit()
        await db.refresh(db_log)
        return db_log

    @staticmethod
    async def get_by_session_id(db: AsyncSession, session_id: str) -> List[WorkflowLog]:
        query = select(WorkflowLog).where(WorkflowLog.session_id == session_id).order_by(WorkflowLog.created_at.asc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_last_checkpoint(db: AsyncSession, session_id: str) -> Optional[WorkflowLog]:
        """Retrieve the last successful checkpoint to enable workflow resume capabilities."""
        query = (
            select(WorkflowLog)
            .where(
                WorkflowLog.session_id == session_id,
                WorkflowLog.status == "completed",
                WorkflowLog.checkpoint_data.isnot(None)
            )
            .order_by(WorkflowLog.created_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        return result.scalars().first()
