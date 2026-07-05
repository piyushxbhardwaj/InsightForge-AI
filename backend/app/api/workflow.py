import json
import asyncio
import time
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from backend.app.database.connection import get_db
from backend.app.models.models import Session
from backend.app.repositories.session_repository import SessionRepository
from backend.app.repositories.workflow_log_repository import WorkflowLogRepository
from backend.app.repositories.report_repository import ReportRepository
from backend.app.repositories.source_repository import SourceRepository
from backend.app.schemas.schemas import ReportCreate, SourceCreate, WorkflowLogCreate
from backend.app.langgraph.graphs.research_graph import research_graph
from backend.app.core.logging import logger

router = APIRouter(prefix="/api/workflow", tags=["Workflow"])

@router.post("/{session_id}")
async def start_workflow(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    Kicks off the research workflow. Sets the status to 'planning'. 
    The client should then listen on the SSE stream to drive progress.
    """
    logger.info(f"Triggering workflow for session: {session_id}")
    session = await SessionRepository.get_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    await SessionRepository.update_status(db, session_id, "planning")
    return {"message": "Workflow started successfully", "session_id": session_id}

@router.get("/{session_id}/stream")
async def stream_workflow_progress(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    Runs the LangGraph research workflow and streams execution progress events
    via Server-Sent Events (SSE). Writes intermediate states, timing metrics,
    sources, and the final report to the SQLite database.
    """
    # Load session details
    session_query = select(Session).where(Session.id == session_id)
    result = await db.execute(session_query)
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_generator():
        logger.info(f"SSE stream connection opened for session {session_id}")
        
        # Prepare the initial LangGraph state
        initial_state = {
            "company_name": session.company_name,
            "website": session.website,
            "research_objective": session.research_objective,
            "search_plan": [],
            "search_results": [],
            "analysed_data": {},
            "quality_assessment": {},
            "report_markdown": "",
            "report_json": {},
            "status": "pending",
            "retry_count": 0,
            "execution_metrics": {},
            "errors": []
        }

        # Setup state variable to keep track of updates across steps
        current_state = initial_state.copy()

        try:
            # Execute LangGraph asynchronously, streaming step updates
            async for event in research_graph.astream(
                initial_state, 
                config={"configurable": {"thread_id": session_id}} # Graph config / recovery thread
            ):
                # An event is a dict of: { "node_name": { ...state updates... } }
                for node_name, state_update in event.items():
                    logger.info(f"Processing event from graph node: {node_name}")
                    
                    # Update local state compilation
                    current_state.update(state_update)
                    
                    # Map graph node to DB status
                    status_mapping = {
                        "planner": "planning",
                        "research": "researching",
                        "analysis": "analyzing",
                        "quality_check": "quality_check",
                        "report_generator": "report_generation"
                    }
                    node_status = status_mapping.get(node_name, "running")
                    
                    # Log state update in database
                    await SessionRepository.update_status(db, session_id, node_status)
                    
                    node_time = current_state.get("execution_metrics", {}).get(node_status, 0.5)
                    log_create = WorkflowLogCreate(
                        node_name=node_name,
                        status="completed",
                        execution_time_seconds=float(node_time),
                        message=f"Node {node_name} completed execution."
                    )
                    await WorkflowLogRepository.create(db, session_id, log_create)

                    # Prepare SSE transmission payload
                    payload = {
                        "node": node_name,
                        "status": "completed",
                        "message": f"Finished {node_status.replace('_', ' ')} phase.",
                        "metrics": current_state.get("execution_metrics", {}),
                        "retry_count": current_state.get("retry_count", 0),
                        "quality_score": current_state.get("quality_assessment", {}).get("overall_score", 0.0)
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                    
                    # Sleep slightly to allow clean animations on the frontend
                    await asyncio.sleep(0.3)

            # --- POST WORKFLOW EXECUTION PERSISTENCE ---
            # Save the final report and sources once graph completes successfully
            logger.info(f"Graph execution complete for {session_id}. Persisting results...")
            
            # Save sources
            sources = current_state.get("search_results", [])
            for s in sources:
                src_in = SourceCreate(
                    title=s.get("title", "Search Link"),
                    url=s.get("url", ""),
                    published_date=s.get("published_date"),
                    source_type=s.get("source_type", "web"),
                    content=s.get("content", ""),
                    relevance_score=s.get("relevance_score", 1.0)
                )
                await SourceRepository.create(db, session_id, src_in)

            # Save report
            report_md = current_state.get("report_markdown", "")
            report_js = current_state.get("report_json", {})
            quality_score = current_state.get("quality_assessment", {}).get("overall_score", 0.90)
            
            rep_in = ReportCreate(
                markdown_content=report_md,
                json_content=report_js,
                confidence_score=float(quality_score)
            )
            await ReportRepository.create(db, session_id, rep_in)
            
            # Final status update
            await SessionRepository.update_status(db, session_id, "completed")
            
            # Final SSE completion message
            final_payload = {
                "node": "completed",
                "status": "completed",
                "message": "Research workflow finished successfully.",
                "metrics": current_state.get("execution_metrics", {}),
                "quality_score": quality_score
            }
            yield f"data: {json.dumps(final_payload)}\n\n"

        except Exception as e:
            logger.error(f"Critical error executing LangGraph workflow: {e}")
            await SessionRepository.update_status(db, session_id, "failed")
            
            log_create = WorkflowLogCreate(
                node_name="system",
                status="failed",
                execution_time_seconds=0.0,
                message=f"System failure: {str(e)}"
            )
            await WorkflowLogRepository.create(db, session_id, log_create)
            
            error_payload = {
                "node": "failed",
                "status": "failed",
                "message": f"Research workflow failed: {str(e)}"
            }
            yield f"data: {json.dumps(error_payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
