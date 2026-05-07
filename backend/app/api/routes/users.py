from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import hash_password
from app.models import User
from app.schemas.crud import UserCreateRequest, UserUpdateRequest


router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    statement = select(User).order_by(User.created_at.desc())
    if current_user.store_id:
        statement = statement.where(User.store_id == current_user.store_id)
    users = list(db.scalars(statement))
    return {"items": [_user_response(u) for u in users]}


@router.post("")
def create_user(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="email already registered")
    user = User(
        store_id=current_user.store_id,
        email=payload.email.strip(),
        full_name=payload.full_name.strip(),
        role=payload.role,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_response(user)


@router.get("/{user_id}")
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    if current_user.store_id and user.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="user belongs to another store")
    return _user_response(user)


@router.patch("/{user_id}")
def update_user(
    user_id: str,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    if current_user.store_id and user.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="user belongs to another store")
    if payload.email is not None:
        user.email = payload.email.strip()
    if payload.full_name is not None:
        user.full_name = payload.full_name.strip()
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return _user_response(user)


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="cannot delete yourself")
    if current_user.store_id and user.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="user belongs to another store")
    db.delete(user)
    db.commit()
    return {"status": "deleted", "user_id": user_id}


def _require_admin(user: User) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="admin role required")


def _user_response(user: User) -> dict:
    return {
        "id": user.id,
        "store_id": user.store_id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
