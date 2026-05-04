from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Conversation
from app.services.handoff_service import HandoffService


router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/{conversation_id}/takeover")
def takeover_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    HandoffService(db).takeover(
        conversation,
        event_type="takeover",
        reason="Atendimento assumido por vendedor humano",
    )
    db.commit()
    return {
        "status": "human_active",
        "conversation_id": conversation.id,
        "ai_enabled": conversation.ai_enabled,
    }


@router.post("/{conversation_id}/release-to-ai")
def release_to_ai(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    HandoffService(db).release_to_ai(conversation)
    db.commit()
    return {
        "status": "ai_active",
        "conversation_id": conversation.id,
        "ai_enabled": conversation.ai_enabled,
    }
