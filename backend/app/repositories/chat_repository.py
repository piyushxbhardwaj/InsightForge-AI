from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from backend.app.models.models import ChatMessage
from backend.app.schemas.schemas import ChatMessageCreate

class ChatRepository:
    @staticmethod
    async def create(db: AsyncSession, session_id: str, message_in: ChatMessageCreate) -> ChatMessage:
        db_message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=message_in.role,
            content=message_in.content
        )
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        return db_message

    @staticmethod
    async def get_by_session_id(db: AsyncSession, session_id: str) -> List[ChatMessage]:
        query = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc())
        result = await db.execute(query)
        return list(result.scalars().all())
