from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_access_token, hash_password
from app.models import Store, User
from app.schemas.dashboard import BootstrapRequest


router = APIRouter(prefix="/setup", tags=["setup"])


@router.get("/status")
def setup_status(db: Session = Depends(get_db)):
    users_count = db.scalar(select(func.count()).select_from(User)) or 0
    return {"needs_setup": users_count == 0}


@router.post("/bootstrap")
def bootstrap(payload: BootstrapRequest, db: Session = Depends(get_db)):
    users_count = db.scalar(select(func.count()).select_from(User)) or 0
    if users_count > 0:
        raise HTTPException(status_code=409, detail="setup already completed")

    store = Store(
        name=payload.store_name.strip(),
        slug=payload.store_slug.strip(),
        document=payload.store_document,
        phone=payload.store_phone,
    )
    db.add(store)
    db.flush()

    admin = User(
        store_id=store.id,
        email=payload.admin_email.strip().lower(),
        full_name=payload.admin_full_name.strip(),
        role="admin",
        hashed_password=hash_password(payload.admin_password),
        is_active=True,
    )
    db.add(admin)
    db.flush()

    token = create_access_token(
        admin.id,
        {"role": admin.role, "store_id": admin.store_id},
    )
    db.commit()
    return {
        "access_token": token,
        "token_type": "bearer",
        "store": _store_response(store),
        "user": {
            "id": admin.id,
            "email": admin.email,
            "full_name": admin.full_name,
            "role": admin.role,
            "store_id": admin.store_id,
        },
    }


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
