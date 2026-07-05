import json
import asyncio
import time
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.session_repository import SessionRepository
from backend.app.repositories.workflow_log_repository import WorkflowLogRepository
from backend.app.repositories.report_repository import ReportRepository
from backend.app.repositories.source_repository import SourceRepository
from backend.app.schemas.schemas import ReportCreate, SourceCreate, WorkflowLogCreate
from backend.app.langgraph.graphs.research_graph import research_graph
from backend.app.core.logging import logger

class WorkflowService:
    @staticmethod
    async def run_workflow_stream(db: AsyncSession, session_id: str) -> AsyncGenerator[str, None]:
        """
        Orchestrates and executes the LangGraph workflow. Streams progress updates
        as Server-Sent Events (SSE) and handles intermediate database updates.
        """
        logger.info(f"[WorkflowService] Initializing stream for session: {session_id}")
        session = await SessionRepository.get_by_id(db, session_id)
        if not session:
            yield f"data: {json.dumps({'node': 'error', 'status': 'failed', 'message': 'Session not found'})}\n\n"
            return

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

        current_state = initial_state.copy()

        try:
            # Run LangGraph streaming
            async for event in research_graph.astream(
                initial_state, 
                config={"configurable": {"thread_id": session_id}}
            ):
                for node_name, state_update in event.items():
                    current_state.update(state_update)
                    
                    status_mapping = {
                        "planner": "planning",
                        "research": "researching",
                        "analysis": "analyzing",
                        "quality_check": "quality_check",
                        "report_generator": "report_generation"
                    }
                    node_status = status_mapping.get(node_name, "running")
                    
                    # Update session status
                    await SessionRepository.update_status(db, session_id, node_status)
                    
                    # Save step log
                    node_time = current_state.get("execution_metrics", {}).get(node_status, 0.5)
                    log_create = WorkflowLogCreate(
                        node_name=node_name,
                        status="completed",
                        execution_time_seconds=float(node_time),
                        message=f"Step {node_status.replace('_', ' ')} completed."
                    )
                    await WorkflowLogRepository.create(db, session_id, log_create)

                    # Yield event back to API controller
                    payload = {
                        "node": node_name,
                        "status": "completed",
                        "message": f"Finished {node_status.replace('_', ' ')} phase.",
                        "metrics": current_state.get("execution_metrics", {}),
                        "retry_count": current_state.get("retry_count", 0),
                        "quality_score": current_state.get("quality_assessment", {}).get("overall_score", 0.0)
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                    await asyncio.sleep(0.1)

            # --- POST EXECUTION DB PERSISTENCE ---
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
            
            # Print Observability Metrics
            metrics = current_state.get("execution_metrics", {})
            total_time = sum(metrics.values())
            logger.info("=" * 40)
            logger.info("    INSIGHTFORGE AI EXECUTION METRICS    ")
            logger.info("=" * 40)
            for node, duration in metrics.items():
                logger.info(f" - {node.capitalize()}: {duration}s")
            logger.info("-" * 40)
            logger.info(f" Total Time: {total_time:.2f}s")
            logger.info(f" Quality Confidence Score: {quality_score * 100:.0f}%")
            logger.info(f" Sources Collected: {len(sources)}")
            logger.info(f" Retries: {current_state.get('retry_count', 0)}")
            logger.info("=" * 40)

            # Set session to completed
            await SessionRepository.update_status(db, session_id, "completed")
            
            final_payload = {
                "node": "completed",
                "status": "completed",
                "message": "Research workflow finished successfully.",
                "metrics": current_state.get("execution_metrics", {}),
                "quality_score": quality_score
            }
            yield f"data: {json.dumps(final_payload)}\n\n"

        except Exception as e:
            logger.error(f"[WorkflowService] Critical error executing graph: {e}")
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
