from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Store, User
from app.schemas.dashboard import StoreUpdateRequest


router = APIRouter(prefix="/store", tags=["store"])


@router.get("/me")
def get_my_store(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store = _get_user_store(db, current_user)
    return _store_response(store)


@router.patch("/me")
def update_my_store(
    payload: StoreUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store = _get_user_store(db, current_user)
    if payload.name is not None:
        store.name = payload.name.strip()
    if payload.document is not None:
        store.document = payload.document
    if payload.phone is not None:
        store.phone = payload.phone
    db.commit()
    db.refresh(store)
    return _store_response(store)


def _get_user_store(db: Session, current_user: User) -> Store:
    if not current_user.store_id:
        raise HTTPException(status_code=403, detail="user has no store")
    store = db.get(Store, current_user.store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="store not found")
    return store


def _store_response(store: Store) -> dict:
    return {
        "id": store.id,
        "name": store.name,
        "slug": store.slug,
        "document": store.document,
        "phone": store.phone,
        "created_at": store.created_at,
        "updated_at": store.updated_at,
    }
