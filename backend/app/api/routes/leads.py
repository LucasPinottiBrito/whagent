from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Lead, User


router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("")
def list_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(Lead).order_by(Lead.updated_at.desc())
    if current_user.store_id:
        statement = statement.where(Lead.store_id == current_user.store_id)
    leads = list(db.scalars(statement))
    return {"items": [_lead_response(lead) for lead in leads]}


@router.get("/{lead_id}")
def get_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="lead not found")
    if current_user.store_id and lead.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="lead belongs to another store")
    return _lead_response(lead)


def _lead_response(lead: Lead) -> dict:
    customer = lead.conversation.customer if lead.conversation else None
    return {
        "id": lead.id,
        "store_id": lead.store_id,
        "customer_id": lead.customer_id,
        "conversation_id": lead.conversation_id,
        "status": lead.status,
        "score": lead.score,
        "intent": lead.intent,
        "vehicle_interest": lead.vehicle_interest,
        "budget_min": lead.budget_min,
        "budget_max": lead.budget_max,
        "payment_type": lead.payment_type,
        "trade_in_vehicle": lead.trade_in_vehicle,
        "interest_summary": lead.interest_summary,
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "phone": customer.phone,
        }
        if customer
        else None,
        "created_at": lead.created_at,
        "updated_at": lead.updated_at,
    }
