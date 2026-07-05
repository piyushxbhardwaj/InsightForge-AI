from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from backend.app.database.connection import get_db
from backend.app.models.models import Session
from backend.app.schemas.schemas import (
    SessionCreate, 
    SessionResponse, 
    SessionDetailResponse,
    CacheCheckResponse
)
from backend.app.repositories.session_repository import SessionRepository
from backend.app.core.logging import logger

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

@router.get("/check-cache", response_model=CacheCheckResponse)
async def check_session_cache(
    company_name: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db)
):
    """Check if a recently completed session exists for the given company name."""
    logger.info(f"Checking cache for company: {company_name}")
    cached = await SessionRepository.get_cached_session(db, company_name)
    if cached:
        logger.info(f"Cache hit: completed session found with ID {cached.id}")
        return CacheCheckResponse(
            has_cached=True,
            cached_session_id=cached.id,
            company_name=cached.company_name,
            created_at=cached.created_at
        )
    return CacheCheckResponse(
        has_cached=False,
        cached_session_id=None,
        company_name=company_name,
        created_at=None
    )

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_in: SessionCreate,
    use_cache: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new research session. If use_cache is True and a recently completed
    session for the same company exists, it returns the cached session immediately.
    """
    logger.info(f"Creating session for {session_in.company_name} (use_cache={use_cache})")
    
    if use_cache:
        cached = await SessionRepository.get_cached_session(db, session_in.company_name)
        if cached:
            logger.info(f"Reusing cached session {cached.id} for {session_in.company_name}")
            return cached

    new_session = await SessionRepository.create(db, session_in)
    logger.info(f"New session created with ID {new_session.id}")
    return new_session

@router.get("", response_model=List[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """Retrieve all research sessions."""
    logger.info("Listing all sessions")
    return await SessionRepository.get_all(db)

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_details(session_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve detailed research session information including reports, sources, and logs."""
    logger.info(f"Fetching details for session: {session_id}")
    
    # Query with selectinload to eagerly load related records in async session
    query = (
        select(Session)
        .where(Session.id == session_id)
        .options(
            selectinload(Session.reports),
            selectinload(Session.sources),
            selectinload(Session.chat_messages),
            selectinload(Session.workflow_logs)
        )
    )
    result = await db.execute(query)
    session = result.scalars().first()
    
    if not session:
        logger.warning(f"Session not found: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
        
    return session
