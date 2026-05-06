from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    get_agent_service,
    get_current_user,
    get_db,
    get_evolution_service,
    require_conversation_access,
)
from app.models import AgentRun, Conversation, HandoffEvent, Lead, Message, User
from app.schemas.conversations import TakeoverRequest
from app.schemas.dashboard import HumanMessageRequest
from app.services.agent_service import AgentService
from app.services.conversation_processing_service import ConversationProcessingService
from app.services.evolution_service import EvolutionService
from app.services.handoff_service import HandoffService


router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(Conversation).order_by(Conversation.updated_at.desc())
    if current_user.store_id:
        statement = statement.where(Conversation.store_id == current_user.store_id)
    conversations = list(db.scalars(statement))
    return {
        "items": [_conversation_summary(db, conversation) for conversation in conversations]
    }


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    require_conversation_access(conversation, current_user)
    return _conversation_detail(db, conversation)


@router.post("/{conversation_id}/messages/human")
def send_human_message(
    conversation_id: str,
    payload: HumanMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    require_conversation_access(conversation, current_user)
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="message content is required")

    message = Message(
        conversation_id=conversation.id,
        direction="outbound",
        sender_type="human",
        content=content,
    )
    db.add(message)
    db.flush()
    if conversation.status != "human_active" or conversation.ai_enabled:
        HandoffService(db).takeover(
            conversation,
            event_type="manual_panel",
            salesperson_id=current_user.id,
        )

    evolution = evolution_service.send_text_message(
        conversation.whatsapp_instance.instance_name,
        conversation.customer.phone,
        content,
    )
    db.commit()
    db.refresh(message)
    return {"message": _message_response(message), "evolution": evolution}


@router.post("/{conversation_id}/ai/enable")
def enable_ai(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    require_conversation_access(conversation, current_user)
    HandoffService(db).release_to_ai(conversation, salesperson_id=current_user.id)
    db.commit()
    return {
        "status": conversation.status,
        "conversation_id": conversation.id,
        "ai_enabled": conversation.ai_enabled,
    }


@router.post("/{conversation_id}/ai/disable")
def disable_ai(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    require_conversation_access(conversation, current_user)
    conversation.status = "ai_disabled"
    conversation.ai_enabled = False
    db.add(
        HandoffEvent(
            conversation_id=conversation.id,
            salesperson_id=current_user.id,
            event_type="ai_disabled",
        )
    )
    db.commit()
    return {
        "status": conversation.status,
        "conversation_id": conversation.id,
        "ai_enabled": conversation.ai_enabled,
    }


@router.post("/{conversation_id}/process-now")
def process_now(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    require_conversation_access(conversation, current_user)
    processing = ConversationProcessingService(
        db=db,
        agent_service=agent_service,
        evolution_service=evolution_service,
    )
    return processing.process(conversation_id)


@router.post("/{conversation_id}/takeover")
def takeover(
    conversation_id: str,
    payload: TakeoverRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    require_conversation_access(conversation, current_user)
    HandoffService(db).takeover(
        conversation,
        event_type="takeover",
        reason=payload.reason if payload else None,
        salesperson_id=current_user.id,
    )
    db.commit()
    return {
        "status": conversation.status,
        "conversation_id": conversation.id,
        "ai_enabled": conversation.ai_enabled,
    }


@router.post("/{conversation_id}/release-to-ai")
def release_to_ai(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    require_conversation_access(conversation, current_user)
    HandoffService(db).release_to_ai(conversation, salesperson_id=current_user.id)
    db.commit()
    return {
        "status": conversation.status,
        "conversation_id": conversation.id,
        "ai_enabled": conversation.ai_enabled,
    }


def _conversation_summary(db: Session, conversation: Conversation) -> dict:
    last_message = db.scalar(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc(), Message.id.desc())
    )
    return {
        "id": conversation.id,
        "status": conversation.status,
        "ai_enabled": conversation.ai_enabled,
        "pending_agent_processing": conversation.pending_agent_processing,
        "last_intent": conversation.last_intent,
        "last_customer_message_at": conversation.last_customer_message_at,
        "last_processing_error": conversation.last_processing_error,
        "customer": {
            "id": conversation.customer.id,
            "name": conversation.customer.name,
            "phone": conversation.customer.phone,
        },
        "whatsapp_instance": {
            "id": conversation.whatsapp_instance.id,
            "instance_name": conversation.whatsapp_instance.instance_name,
            "phone": conversation.whatsapp_instance.phone,
        },
        "lead": _lead_response(conversation.lead) if conversation.lead else None,
        "last_message": _message_response(last_message) if last_message else None,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }


def _conversation_detail(db: Session, conversation: Conversation) -> dict:
    messages = list(
        db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at, Message.id)
        )
    )
    agent_runs = list(
        db.scalars(
            select(AgentRun)
            .where(AgentRun.conversation_id == conversation.id)
            .order_by(AgentRun.created_at.desc())
        )
    )
    handoff_events = list(
        db.scalars(
            select(HandoffEvent)
            .where(HandoffEvent.conversation_id == conversation.id)
            .order_by(HandoffEvent.created_at.desc())
        )
    )
    payload = _conversation_summary(db, conversation)
    payload.update(
        {
            "messages": [_message_response(message) for message in messages],
            "agent_runs": [_agent_run_response(run) for run in agent_runs],
            "handoff_events": [
                _handoff_event_response(event) for event in handoff_events
            ],
        }
    )
    return payload


def _message_response(message: Message) -> dict:
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "direction": message.direction,
        "sender_type": message.sender_type,
        "content": message.content,
        "evolution_message_id": message.evolution_message_id,
        "created_at": message.created_at,
    }


def _lead_response(lead: Lead) -> dict:
    return {
        "id": lead.id,
        "status": lead.status,
        "score": lead.score,
        "intent": lead.intent,
        "vehicle_interest": lead.vehicle_interest,
        "budget_min": lead.budget_min,
        "budget_max": lead.budget_max,
        "payment_type": lead.payment_type,
        "trade_in_vehicle": lead.trade_in_vehicle,
        "interest_summary": lead.interest_summary,
        "updated_at": lead.updated_at,
    }


def _agent_run_response(agent_run: AgentRun) -> dict:
    return {
        "id": agent_run.id,
        "input_text": agent_run.input_text,
        "output_text": agent_run.output_text,
        "model": agent_run.model,
        "tools_used": agent_run.tools_used,
        "status": agent_run.status,
        "error": agent_run.error,
        "created_at": agent_run.created_at,
        "updated_at": agent_run.updated_at,
    }


def _handoff_event_response(event: HandoffEvent) -> dict:
    return {
        "id": event.id,
        "event_type": event.event_type,
        "salesperson_id": event.salesperson_id,
        "reason": event.reason,
        "metadata": event.event_metadata,
        "created_at": event.created_at,
    }
