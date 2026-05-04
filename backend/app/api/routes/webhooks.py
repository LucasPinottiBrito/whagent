from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_conversation_queue, get_db
from app.models import WhatsAppInstance
from app.schemas.webhook import EvolutionWebhookResponse
from app.services.conversation_queue import ConversationQueue
from app.services.conversation_service import ConversationService
from app.services.handoff_service import HandoffService
from app.services.webhook_parser import WebhookParseError, parse_evolution_webhook
from app.utils.datetime import utcnow


router = APIRouter(prefix="/webhooks/evolution", tags=["webhooks"])


@router.post("/{instance_name}", response_model=EvolutionWebhookResponse)
def receive_evolution_webhook(
    instance_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    queue: ConversationQueue = Depends(get_conversation_queue),
):
    instance = db.scalar(
        select(WhatsAppInstance).where(
            WhatsAppInstance.instance_name == instance_name,
            WhatsAppInstance.active.is_(True),
        )
    )
    if instance is None:
        raise HTTPException(status_code=404, detail="whatsapp instance not found")

    try:
        parsed = parse_evolution_webhook(payload)
    except WebhookParseError:
        return EvolutionWebhookResponse(status="ignored")

    conversation_service = ConversationService(db)
    customer = conversation_service.get_or_create_customer(
        store_id=instance.store_id,
        phone=parsed.phone,
        name=parsed.customer_name,
    )
    conversation = conversation_service.get_or_create_conversation(
        customer=customer, instance=instance
    )

    if parsed.from_me:
        if parsed.sent_by_agent:
            db.commit()
            return EvolutionWebhookResponse(
                status="ignored_agent_echo",
                conversation_id=conversation.id,
                message_id=parsed.message_id,
            )

        conversation_service.add_message(
            conversation=conversation,
            direction="outbound",
            sender_type="human",
            content=parsed.text,
            evolution_message_id=parsed.message_id,
            raw_payload=payload,
        )
        HandoffService(db).takeover(
            conversation,
            event_type="manual_from_me",
            reason="Mensagem manual detectada pela Evolution API",
        )
        db.commit()
        return EvolutionWebhookResponse(
            status="human_takeover",
            conversation_id=conversation.id,
            message_id=parsed.message_id,
        )

    message = conversation_service.add_message(
        conversation=conversation,
        direction="inbound",
        sender_type="customer",
        content=parsed.text,
        evolution_message_id=parsed.message_id,
        raw_payload=payload,
    )
    conversation.last_customer_message_at = utcnow()
    conversation.pending_agent_processing = True
    queue.schedule_conversation(conversation.id)
    db.commit()

    return EvolutionWebhookResponse(
        status="scheduled",
        conversation_id=conversation.id,
        message_id=message.id,
        scheduled=True,
    )
