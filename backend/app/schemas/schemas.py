from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Source Schemas ---
class SourceBase(BaseModel):
    title: str
    url: str
    published_date: Optional[str] = None
    source_type: str = "web"
    content: str
    relevance_score: float = 1.0

class SourceCreate(SourceBase):
    pass

class SourceResponse(SourceBase):
    id: str
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Report Schemas ---
class ReportBase(BaseModel):
    markdown_content: str
    json_content: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0

class ReportCreate(ReportBase):
    pass

class ReportResponse(ReportBase):
    id: str
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- ChatMessage Schemas ---
class ChatMessageBase(BaseModel):
    role: str # user, assistant
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: str
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- WorkflowLog Schemas ---
class WorkflowLogBase(BaseModel):
    node_name: str
    status: str # started, completed, failed
    execution_time_seconds: float = 0.0
    checkpoint_data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class WorkflowLogCreate(WorkflowLogBase):
    pass

class WorkflowLogResponse(WorkflowLogBase):
    id: str
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Session Schemas ---
class SessionBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    website: str = Field(..., min_length=3, max_length=255)
    research_objective: str = Field(..., min_length=5)

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SessionDetailResponse(SessionResponse):
    reports: List[ReportResponse] = []
    sources: List[SourceResponse] = []
    workflow_logs: List[WorkflowLogResponse] = []
    chat_messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True

# --- Cache Response Schema ---
class CacheCheckResponse(BaseModel):
    has_cached: bool
    cached_session_id: Optional[str] = None
    company_name: str
    created_at: Optional[datetime] = None
