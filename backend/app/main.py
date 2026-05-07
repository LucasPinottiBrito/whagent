from fastapi import FastAPI
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth,
    conversations,
    customers,
    dashboard,
    health,
    internal,
    leads,
    store,
    users,
    webhooks,
    whatsapp_instances,
)
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Store, User


configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.app_debug)


def ensure_default_admin() -> None:
    db = SessionLocal()
    try:
        admin_count = db.scalar(select(func.count()).select_from(User).where(User.role == "admin")) or 0
        if admin_count > 0:
            return

        store = db.scalar(select(Store).where(Store.slug == "loja-padrao"))
        if store is None:
            store = Store(name="Loja Padrão", slug="loja-padrao")
            db.add(store)
            db.flush()

        admin = User(
            store_id=store.id,
            email="admin@whagent.local",
            full_name="Administrador",
            role="admin",
            hashed_password=hash_password("admin123"),
            is_active=True,
        )
        db.add(admin)
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def startup_tasks() -> None:
    if settings.app_env == "test":
        return
    try:
        ensure_default_admin()
    except OperationalError:
        # During startup before migrations, tables may not exist yet.
        pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list if settings.is_production else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api/auth")
app.include_router(store.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(whatsapp_instances.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
app.include_router(internal.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(customers.router, prefix="/api")

if not settings.is_production:
    from app.api.routes import debug

    app.include_router(debug.router, prefix="/api")

