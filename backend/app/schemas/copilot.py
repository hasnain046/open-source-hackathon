# Module: app.schemas.copilot
# Description: Pydantic validation schemas for AI Economist Copilot responses.

from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional


class ChatRequestSchema(BaseModel):
    conversation_id: Optional[UUID] = None
    message: str
    mode: Optional[str] = "analyst"  # "economist", "analyst", "executive"


class ChatMessageResponseSchema(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class SourceAttributionSchema(BaseModel):
    engine: str
    source_type: str
    status: str


class ChatResponseSchema(BaseModel):
    conversation_id: UUID
    reply: str
    history: List[ChatMessageResponseSchema]
    sources: List[SourceAttributionSchema]
    confidence_score: float
    confidence_indicator: str
    generated_by: str  # "LLM" or "NLG Fallback"


class ConversationListResponseSchema(BaseModel):
    id: UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


ChatQuerySchema = ChatRequestSchema
