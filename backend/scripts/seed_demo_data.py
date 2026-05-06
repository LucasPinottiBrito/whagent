import os

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Store, User, WhatsAppInstance


def seed() -> None:
    db = SessionLocal()
    try:
        store = db.scalar(select(Store).where(Store.slug == "loja-demo"))
        if store is None:
            store = Store(
                name="Loja Demo",
                slug="loja-demo",
                document="00000000000100",
                phone="5511999999999",
            )
            db.add(store)
            db.flush()

        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        admin = db.scalar(select(User).where(User.email == admin_email))
        if admin is None:
            db.add(
                User(
                    store_id=store.id,
                    email=admin_email,
                    full_name="Admin Demo",
                    role="admin",
                    hashed_password=hash_password(admin_password),
                    is_active=True,
                )
            )

        seller = db.scalar(select(User).where(User.email == "seller@example.com"))
        if seller is None:
            db.add(
                User(
                    store_id=store.id,
                    email="seller@example.com",
                    full_name="Vendedor Demo",
                    role="salesperson",
                    hashed_password=hash_password("seller123"),
                    is_active=True,
                )
            )

        instance = db.scalar(
            select(WhatsAppInstance).where(
                WhatsAppInstance.instance_name == "demo-instance"
            )
        )
        if instance is None:
            db.add(
                WhatsAppInstance(
                    store_id=store.id,
                    instance_name="demo-instance",
                    phone="5511999999999",
                    webhook_secret="dev-evolution-webhook-secret",
                    active=True,
                )
            )
        db.commit()
        print("Seed demo criado: loja, admin, vendedor e instancia WhatsApp.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
