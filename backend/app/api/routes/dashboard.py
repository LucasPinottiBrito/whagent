from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Conversation, Customer, Lead, User, WhatsAppInstance


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store_id = current_user.store_id
    return {
        "customers_total": _count(db, Customer, store_id),
        "conversations_total": _count(db, Conversation, store_id),
        "leads_total": _count(db, Lead, store_id),
        "instances_total": _count(db, WhatsAppInstance, store_id),
        "ai_active_conversations": _count_conversations_by_status(
            db, store_id, "ai_active"
        ),
        "human_active_conversations": _count_conversations_by_status(
            db, store_id, "human_active"
        ),
        "pending_conversations": _count_pending_conversations(db, store_id),
    }


def _count(db: Session, model, store_id: str | None) -> int:
    statement = select(func.count()).select_from(model)
    if store_id:
        statement = statement.where(model.store_id == store_id)
    return int(db.scalar(statement) or 0)


def _count_conversations_by_status(
    db: Session, store_id: str | None, status: str
) -> int:
    statement = select(func.count()).select_from(Conversation).where(
        Conversation.status == status
    )
    if store_id:
        statement = statement.where(Conversation.store_id == store_id)
    return int(db.scalar(statement) or 0)


def _count_pending_conversations(db: Session, store_id: str | None) -> int:
    statement = select(func.count()).select_from(Conversation).where(
        Conversation.pending_agent_processing.is_(True)
    )
    if store_id:
        statement = statement.where(Conversation.store_id == store_id)
    return int(db.scalar(statement) or 0)
