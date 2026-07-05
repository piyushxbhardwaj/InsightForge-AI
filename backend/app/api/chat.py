from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.connection import get_db
from backend.app.schemas.schemas import ChatMessageCreate, ChatMessageResponse
from backend.app.repositories.chat_repository import ChatRepository
from backend.app.services.chat_service import ChatService
from backend.app.core.logging import logger

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.get("/{session_id}", response_model=list[ChatMessageResponse])
async def get_chat_history(session_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve all follow-up chat messages for a research session."""
    logger.info(f"[Chat Router] Retrieving chat history for session: {session_id}")
    return await ChatRepository.get_by_session_id(db, session_id)

@router.post("/{session_id}", response_model=ChatMessageResponse)
async def send_chat_query(
    session_id: str,
    message_in: ChatMessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Submit a follow-up query to the sales research assistant."""
    logger.info(f"[Chat Router] Received query for session: {session_id}")
    # Delegating to ChatService
    return await ChatService.process_chat_message(db, session_id, message_in)
