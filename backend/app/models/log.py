# Module: app.models.log
# Description: SQLAlchemy database models defining system audits and AI economist chat history entries.

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String, nullable=False, index=True)
    details = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class CopilotConversation(Base):
    __tablename__ = "copilot_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ORM Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("CopilotMessage", back_populates="conversation", cascade="all, delete-orphan")


class CopilotMessage(Base):
    __tablename__ = "copilot_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("copilot_conversations.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user', 'assistant'
    content = Column(String, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)

    # ORM Relationships
    conversation = relationship("CopilotConversation", back_populates="messages")
