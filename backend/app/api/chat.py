import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.connection import get_db
from backend.app.schemas.schemas import ChatMessageCreate, ChatMessageResponse
from backend.app.repositories.chat_repository import ChatRepository
from backend.app.repositories.report_repository import ReportRepository
from backend.app.services.llm_service import LLMService
from backend.app.prompts.chat_prompt import CHAT_PROMPT_TEMPLATE
from backend.app.core.logging import logger

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.get("/{session_id}", response_model=list[ChatMessageResponse])
async def get_chat_history(session_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve all follow-up chat messages for a research session."""
    logger.info(f"Retrieving chat history for session: {session_id}")
    return await ChatRepository.get_by_session_id(db, session_id)

@router.post("/{session_id}", response_model=ChatMessageResponse)
async def send_chat_query(
    session_id: str,
    message_in: ChatMessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a follow-up query. Restricts the LLM answer strictly to report context
    to ensure zero hallucination, and saves the message exchange in the DB.
    """
    logger.info(f"Received chat query for session {session_id}: {message_in.content[:50]}...")
    
    # 1. Fetch the compiled report for this session
    report = await ReportRepository.get_by_session_id(db, session_id)
    if not report:
        logger.warning(f"Report not found for chat session: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research report not compiled yet. Complete the workflow before chatting."
        )

    # Convert the report JSON content or markdown to string context
    # Injecting JSON content is much smaller and cleaner than full markdown!
    if report.json_content:
        report_context = json.dumps(report.json_content, indent=2)
    else:
        report_context = report.markdown_content

    # 2. Save user message to database
    user_msg_in = ChatMessageCreate(role="user", content=message_in.content)
    await ChatRepository.create(db, session_id, user_msg_in)

    # 3. Format the chat prompt
    prompt = CHAT_PROMPT_TEMPLATE.format(
        report_context=report_context,
        user_question=message_in.content
    )

    # 4. Invoke LLM in chat mode
    llm_service = LLMService()
    ai_response_content = await llm_service.call_llm(
        prompt=prompt,
        system_prompt="You are a strict QA assistant. Answer only using the context. If not present, reply: 'This information is not available in the current research report.'",
        category="chat"
    )
    
    # 5. Clean up response string
    clean_ai_response = ai_response_content.strip()

    # 6. Save assistant response to database
    ai_msg_in = ChatMessageCreate(role="assistant", content=clean_ai_response)
    db_ai_msg = await ChatRepository.create(db, session_id, ai_msg_in)
    
    logger.info(f"Saved AI chat answer for session {session_id}")
    return db_ai_msg
