from sqlalchemy.orm import Session

from app.models import Conversation, HandoffEvent


class HandoffService:
    def __init__(self, db: Session):
        self.db = db

    def takeover(
        self,
        conversation: Conversation,
        *,
        event_type: str = "takeover",
        reason: str | None = None,
        salesperson_id: str | None = None,
        metadata: dict | None = None,
    ) -> HandoffEvent:
        conversation.status = "human_active"
        conversation.ai_enabled = False
        event = HandoffEvent(
            conversation_id=conversation.id,
            salesperson_id=salesperson_id,
            event_type=event_type,
            reason=reason,
            event_metadata=metadata,
        )
        self.db.add(event)
        self.db.flush()
        return event

    def release_to_ai(
        self,
        conversation: Conversation,
        *,
        salesperson_id: str | None = None,
        reason: str | None = None,
    ) -> HandoffEvent:
        conversation.status = "ai_active"
        conversation.ai_enabled = True
        event = HandoffEvent(
            conversation_id=conversation.id,
            salesperson_id=salesperson_id,
            event_type="release_to_ai",
            reason=reason,
        )
        self.db.add(event)
        self.db.flush()
        return event
