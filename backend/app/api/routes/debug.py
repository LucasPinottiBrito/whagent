from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    get_agent_service,
    get_conversation_queue_service,
    get_db,
    get_evolution_service,
)
from app.models import AgentRun, Conversation, HandoffEvent, Lead, Message
from app.schemas.debug import DebugRuntimePatch, SimulateInboundRequest
from app.services.agent_service import AgentService
from app.services.conversation_processing_service import ConversationProcessingService
from app.services.conversation_queue_service import ConversationQueueService
from app.services.evolution_service import EvolutionService
from app.services.evolution_webhook_service import EvolutionWebhookService
from app.services.runtime_state import reset_runtime_state, runtime_state


router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/runtime")
def get_runtime():
    return {
        "ai_runtime_enabled": runtime_state.ai_runtime_enabled,
        "allow_from_me_as_inbound": runtime_state.allow_from_me_as_inbound,
    }


@router.patch("/runtime")
def patch_runtime(payload: DebugRuntimePatch):
    if payload.ai_runtime_enabled is not None:
        runtime_state.ai_runtime_enabled = payload.ai_runtime_enabled
    if payload.allow_from_me_as_inbound is not None:
        runtime_state.allow_from_me_as_inbound = payload.allow_from_me_as_inbound
    return get_runtime()


@router.post("/runtime/reset")
def reset_runtime():
    reset_runtime_state()
    return get_runtime()


@router.post("/modes/self-group")
def enable_self_group_mode():
    runtime_state.allow_from_me_as_inbound = True
    return get_runtime()


@router.post("/modes/external-tester")
def enable_external_tester_mode():
    runtime_state.allow_from_me_as_inbound = False
    return get_runtime()


@router.post("/evolution/simulate-inbound")
def simulate_inbound(
    payload: SimulateInboundRequest,
    db: Session = Depends(get_db),
    queue: ConversationQueueService = Depends(get_conversation_queue_service),
    agent_service: AgentService = Depends(get_agent_service),
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    message_id = payload.message_id or f"debug-{payload.phone}-{abs(hash(payload.text))}"
    evolution_payload = {
        "event": "MESSAGES_UPSERT",
        "data": {
            "key": {
                "id": message_id,
                "remoteJid": f"{payload.phone}@s.whatsapp.net",
                "fromMe": False,
            },
            "pushName": payload.push_name,
            "message": {"conversation": payload.text},
        },
    }
    result = EvolutionWebhookService(db=db, queue=queue).handle(
        instance_name=payload.instance_name,
        payload=evolution_payload,
        webhook_secret=payload.webhook_secret,
    )
    processing = None
    if payload.process_now and result.get("conversation_id"):
        processing = ConversationProcessingService(
            db=db,
            agent_service=agent_service,
            evolution_service=evolution_service,
        ).process(result["conversation_id"])
    return {"webhook": result, "processing": processing}


@router.get("/conversations/{conversation_id}")
def conversation_timeline(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    messages = list(
        db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        )
    )
    return {
        "conversation": _model_dict(conversation),
        "customer": _model_dict(conversation.customer),
        "messages": [_model_dict(message) for message in messages],
        "lead": _model_dict(db.scalar(select(Lead).where(Lead.conversation_id == conversation.id))),
        "agent_runs": [
            _model_dict(item)
            for item in db.scalars(
                select(AgentRun)
                .where(AgentRun.conversation_id == conversation.id)
                .order_by(AgentRun.created_at)
            )
        ],
        "handoff_events": [
            _model_dict(item)
            for item in db.scalars(
                select(HandoffEvent)
                .where(HandoffEvent.conversation_id == conversation.id)
                .order_by(HandoffEvent.created_at)
            )
        ],
        "state": {
            "status": conversation.status,
            "ai_enabled": conversation.ai_enabled,
            "pending_agent_processing": conversation.pending_agent_processing,
            "last_processing_error": conversation.last_processing_error,
        },
    }


@router.post("/conversations/{conversation_id}/ai/disable")
def disable_ai(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    conversation.ai_enabled = False
    conversation.status = "ai_disabled"
    db.commit()
    return {"status": conversation.status, "ai_enabled": conversation.ai_enabled}


@router.post("/conversations/{conversation_id}/ai/enable")
def enable_ai(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    conversation.ai_enabled = True
    conversation.status = "ai_active"
    db.commit()
    return {"status": conversation.status, "ai_enabled": conversation.ai_enabled}


@router.post("/conversations/{conversation_id}/human/takeover")
def debug_takeover(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    from app.services.handoff_service import HandoffService

    HandoffService(db).takeover(conversation, event_type="debug_takeover")
    db.commit()
    return {"status": conversation.status, "ai_enabled": conversation.ai_enabled}


@router.post("/conversations/{conversation_id}/human/release")
def debug_release(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    from app.services.handoff_service import HandoffService

    HandoffService(db).release_to_ai(conversation)
    db.commit()
    return {"status": conversation.status, "ai_enabled": conversation.ai_enabled}


def _model_dict(model):
    if model is None:
        return None
    data = {}
    for column in model.__table__.columns:
        value = getattr(model, column.key)
        data[column.key] = value.isoformat() if hasattr(value, "isoformat") else value
    return data
