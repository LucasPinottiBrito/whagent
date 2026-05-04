import os

from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import Salesperson, Store, User, WhatsAppInstance


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        store = db.scalar(select(Store).where(Store.slug == "loja-demo"))
        if store is None:
            store = Store(
                name="Loja Demo",
                slug="loja-demo",
                phone="5511999999999",
            )
            db.add(store)
            db.flush()

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
                    active=True,
                )
            )

        salesperson = db.scalar(
            select(Salesperson).where(Salesperson.email == "ana@example.com")
        )
        if salesperson is None:
            db.add(
                Salesperson(
                    store_id=store.id,
                    name="Ana Vendedora",
                    email="ana@example.com",
                    phone="5511988887777",
                    active=True,
                    specialty="sedans",
                )
            )

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

        db.commit()
        print("Seed concluido: admin, loja demo e instancia demo prontos.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
