from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Message, WhatsAppInstance
from app.services.conversation_queue_service import ConversationQueueService
from app.services.conversation_service import ConversationService
from app.services.handoff_service import HandoffService
from app.services.message_origin_policy import (
    MessageOrigin,
    MessageOriginPolicy,
    RuntimeOriginConfig,
)
from app.services.runtime_state import runtime_state
from app.services.webhook_parser import EvolutionWebhookParser, WebhookParseError
from app.utils.datetime import utcnow


class WebhookAuthError(ValueError):
    pass


class WhatsAppInstanceNotFoundError(ValueError):
    pass


class EvolutionWebhookService:
    def __init__(self, *, db: Session, queue: ConversationQueueService):
        self.db = db
        self.queue = queue
        self.parser = EvolutionWebhookParser()

    def handle(
        self,
        *,
        instance_name: str,
        payload: dict,
        webhook_secret: str | None,
    ) -> dict:
        instance = self.db.scalar(
            select(WhatsAppInstance).where(
                WhatsAppInstance.instance_name == instance_name,
                WhatsAppInstance.active.is_(True),
            )
        )
        if instance is None:
            raise WhatsAppInstanceNotFoundError("whatsapp instance not found")
        if instance.webhook_secret and webhook_secret != instance.webhook_secret:
            raise WebhookAuthError("invalid webhook secret")

        try:
            parsed = self.parser.parse(payload)
        except WebhookParseError:
            return {"status": "ignored_invalid"}

        if parsed.message_id and self._message_exists(parsed.message_id):
            return {"status": "duplicate", "message_id": parsed.message_id}

        conversation_service = ConversationService(self.db)
        customer = conversation_service.get_or_create_customer(
            store_id=instance.store_id,
            phone=parsed.phone,
            name=parsed.push_name,
        )
        conversation = conversation_service.get_or_create_conversation(
            customer=customer, instance=instance
        )
        policy = MessageOriginPolicy(
            RuntimeOriginConfig(
                allow_from_me_as_inbound=runtime_state.allow_from_me_as_inbound
            )
        )
        origin = policy.classify(
            from_me=parsed.from_me,
            sent_by_agent=parsed.sent_by_agent,
            source=parsed.source,
        )

        if origin == MessageOrigin.AGENT_ECHO_IGNORE:
            self.db.commit()
            return {
                "status": "ignored_agent_echo",
                "conversation_id": conversation.id,
                "message_id": parsed.message_id,
            }

        try:
            if origin == MessageOrigin.HUMAN_OUTBOUND_TAKEOVER:
                conversation_service.add_message(
                    conversation=conversation,
                    direction="outbound",
                    sender_type="human",
                    content=parsed.text,
                    evolution_message_id=parsed.message_id,
                    raw_payload=payload,
                )
                HandoffService(self.db).takeover(
                    conversation,
                    event_type="manual_from_me",
                    reason="Mensagem manual detectada via Evolution",
                )
                self.db.commit()
                return {
                    "status": "human_takeover",
                    "conversation_id": conversation.id,
                    "message_id": parsed.message_id,
                }

            if origin == MessageOrigin.CUSTOMER_INBOUND:
                message = conversation_service.add_message(
                    conversation=conversation,
                    direction="inbound",
                    sender_type="customer",
                    content=parsed.text,
                    evolution_message_id=parsed.message_id,
                    raw_payload=payload,
                )
                conversation.last_customer_message_at = utcnow()
                scheduled = False
                if conversation.ai_enabled and conversation.status == "ai_active":
                    conversation.pending_agent_processing = True
                    self.queue.schedule_conversation(conversation.id)
                    scheduled = True
                self.db.commit()
                return {
                    "status": "scheduled" if scheduled else "saved",
                    "conversation_id": conversation.id,
                    "message_id": message.id,
                    "scheduled": scheduled,
                }
        except IntegrityError:
            self.db.rollback()
            if parsed.message_id:
                return {"status": "duplicate", "message_id": parsed.message_id}
            raise

        self.db.commit()
        return {"status": "ignored_from_me", "conversation_id": conversation.id}

    def _message_exists(self, evolution_message_id: str) -> bool:
        return (
            self.db.scalar(
                select(Message.id).where(Message.evolution_message_id == evolution_message_id)
            )
            is not None
        )
