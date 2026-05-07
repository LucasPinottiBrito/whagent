import os
import sys

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Store, User


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required env var: {name}")
    return value


def bootstrap_admin() -> None:
    db = SessionLocal()
    try:
        users_count = db.scalar(select(func.count()).select_from(User)) or 0
        if users_count > 0:
            print("users already exist; skipping admin bootstrap")
            return

        store_name = _required_env("BOOTSTRAP_STORE_NAME")
        store_slug = _required_env("BOOTSTRAP_STORE_SLUG")
        admin_email = _required_env("BOOTSTRAP_ADMIN_EMAIL").lower()
        admin_password = _required_env("BOOTSTRAP_ADMIN_PASSWORD")
        admin_full_name = os.getenv("BOOTSTRAP_ADMIN_FULL_NAME", "Admin").strip() or "Admin"
        store_document = os.getenv("BOOTSTRAP_STORE_DOCUMENT")
        store_phone = os.getenv("BOOTSTRAP_STORE_PHONE")

        store = Store(
            name=store_name,
            slug=store_slug,
            document=store_document,
            phone=store_phone,
        )
        db.add(store)
        db.flush()

        admin = User(
            store_id=store.id,
            email=admin_email,
            full_name=admin_full_name,
            role="admin",
            hashed_password=hash_password(admin_password),
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print(f"admin bootstrap completed for {admin_email}")
    finally:
        db.close()


if __name__ == "__main__":
    try:
        bootstrap_admin()
    except Exception as exc:
        print(f"bootstrap admin failed: {exc}", file=sys.stderr)
        raise
