import json
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from backend.app.models.models import ChatMessage
from backend.app.schemas.schemas import ChatMessageCreate
from backend.app.repositories.chat_repository import ChatRepository
from backend.app.repositories.report_repository import ReportRepository
from backend.app.services.llm_service import LLMService
from backend.app.prompts.chat_prompt import CHAT_PROMPT_TEMPLATE
from backend.app.core.logging import logger

class ChatService:
    @staticmethod
    async def process_chat_message(
        db: AsyncSession, 
        session_id: str, 
        message_in: ChatMessageCreate
    ) -> ChatMessage:
        """
        Loads session report, compiles restricted prompts, calls LLM, 
        and saves exchange to repository.
        """
        logger.info(f"[ChatService] Processing message for session: {session_id}")
        
        # Load report context
        report = await ReportRepository.get_by_session_id(db, session_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research report not compiled yet."
            )

        if report.json_content:
            report_context = json.dumps(report.json_content, indent=2)
        else:
            report_context = report.markdown_content

        # Save user message
        user_msg = ChatMessageCreate(role="user", content=message_in.content)
        await ChatRepository.create(db, session_id, user_msg)

        # Format prompt
        prompt = CHAT_PROMPT_TEMPLATE.format(
            report_context=report_context,
            user_question=message_in.content
        )

        # Invoke LLM
        llm_service = LLMService()
        response = await llm_service.call_llm(
            prompt=prompt,
            system_prompt="You are a strict QA assistant. Answer only using context.",
            category="chat"
        )
        
        clean_response = response.strip()

        # Save and return assistant response
        ai_msg = ChatMessageCreate(role="assistant", content=clean_response)
        return await ChatRepository.create(db, session_id, ai_msg)
