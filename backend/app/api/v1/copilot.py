# Module: app.api.v1.copilot
# Description: API Router handling AI economist natural language Copilot chat endpoints.

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.copilot import (
    ChatRequestSchema,
    ChatResponseSchema,
    ConversationListResponseSchema,
    ChatMessageResponseSchema
)
from app.services.copilot_service import CopilotService

router = APIRouter(prefix="/copilot", tags=["AI Economist Copilot"])


@router.post("/chat", response_model=ChatResponseSchema)
def submit_chat_message(
    payload: ChatRequestSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a natural language question to the AI Economist Copilot."""
    payload_dict = {
        "conversation_id": payload.conversation_id,
        "message": payload.message,
        "mode": payload.mode
    }
    return CopilotService.submit_user_message(db, current_user.id, payload_dict)


@router.get("/conversations", response_model=List[ConversationListResponseSchema])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all active conversation session headers for the current user."""
    return CopilotService.get_user_conversations(db, current_user.id)


@router.get("/conversations/{conversation_id}/messages", response_model=List[ChatMessageResponseSchema])
def get_conversation_history(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve the full chronological message log/history for a specific conversation session."""
    # Verify conversation belongs to user
    from app.models.log import CopilotConversation
    conv = db.query(CopilotConversation).filter(CopilotConversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation session not found")
        
    if conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation session")
        
    return CopilotService.get_conversation_messages(db, conversation_id)
