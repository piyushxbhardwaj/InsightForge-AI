from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.connection import get_db
from backend.app.repositories.session_repository import SessionRepository
from backend.app.services.workflow_service import WorkflowService
from backend.app.core.logging import logger

router = APIRouter(prefix="/api/workflow", tags=["Workflow"])

@router.post("/{session_id}")
async def start_workflow(session_id: str, db: AsyncSession = Depends(get_db)):
    """Kicks off the research workflow by updating status to 'planning'."""
    logger.info(f"[Workflow Router] Triggering workflow for session: {session_id}")
    session = await SessionRepository.get_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    await SessionRepository.update_status(db, session_id, "planning")
    return {"message": "Workflow started successfully", "session_id": session_id}

@router.get("/{session_id}/stream")
async def stream_workflow_progress(session_id: str, db: AsyncSession = Depends(get_db)):
    """Runs the LangGraph research workflow and streams progress events using SSE."""
    logger.info(f"[Workflow Router] Opening progress stream for: {session_id}")
    
    # Delegating to WorkflowService
    event_generator = WorkflowService.run_workflow_stream(db, session_id)
    return StreamingResponse(event_generator, media_type="text/event-stream")
