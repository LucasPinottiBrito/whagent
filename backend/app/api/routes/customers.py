from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Customer, User
from app.schemas.crud import CustomerUpdateRequest


router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("")
def list_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(Customer).order_by(Customer.updated_at.desc())
    if current_user.store_id:
        statement = statement.where(Customer.store_id == current_user.store_id)
    customers = list(db.scalars(statement))
    return {"items": [_customer_response(c) for c in customers]}


@router.get("/{customer_id}")
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")
    if current_user.store_id and customer.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="customer belongs to another store")
    return _customer_response(customer)


@router.patch("/{customer_id}")
def update_customer(
    customer_id: str,
    payload: CustomerUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")
    if current_user.store_id and customer.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="customer belongs to another store")
    if payload.name is not None:
        customer.name = payload.name.strip()
    if payload.phone is not None:
        customer.phone = payload.phone.strip()
    db.commit()
    db.refresh(customer)
    return _customer_response(customer)


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")
    if current_user.store_id and customer.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="customer belongs to another store")
    db.delete(customer)
    db.commit()
    return {"status": "deleted", "customer_id": customer_id}


def _customer_response(customer: Customer) -> dict:
    return {
        "id": customer.id,
        "store_id": customer.store_id,
        "phone": customer.phone,
        "name": customer.name,
        "last_seen_at": customer.last_seen_at,
        "created_at": customer.created_at,
        "updated_at": customer.updated_at,
    }
