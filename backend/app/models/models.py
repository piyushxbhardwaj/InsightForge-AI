from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.app.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_name = Column(String(255), nullable=False, index=True)
    website = Column(String(255), nullable=False)
    research_objective = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending") # pending, planning, researching, analyzing, quality_check, report_generation, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    reports = relationship("Report", back_populates="session", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="session", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    workflow_logs = relationship("WorkflowLog", back_populates="session", cascade="all, delete-orphan")

class Source(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    url = Column(Text, nullable=False)
    published_date = Column(String(100), nullable=True)
    source_type = Column(String(50), nullable=False, default="web") # web, news, blog, etc.
    content = Column(Text, nullable=False)
    relevance_score = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    session = relationship("Session", back_populates="sources")

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    markdown_content = Column(Text, nullable=False)
    json_content = Column(JSON, nullable=True) # Will store the parsed JSON report details
    confidence_score = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    session = relationship("Session", back_populates="reports")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False) # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    session = relationship("Session", back_populates="chat_messages")

class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    node_name = Column(String(100), nullable=False) # planner, research, analysis, etc.
    status = Column(String(50), nullable=False) # started, completed, failed
    execution_time_seconds = Column(Float, nullable=False, default=0.0)
    checkpoint_data = Column(JSON, nullable=True) # Serialized state checkpoint for resume capability
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    session = relationship("Session", back_populates="workflow_logs")
