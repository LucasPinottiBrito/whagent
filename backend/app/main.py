from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth,
    conversations,
    dashboard,
    health,
    internal,
    leads,
    setup,
    store,
    webhooks,
    whatsapp_instances,
)
from app.core.config import get_settings
from app.core.logging import configure_logging


configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.app_debug)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(setup.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(store.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(whatsapp_instances.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
app.include_router(internal.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(leads.router, prefix="/api")

if not settings.is_production:
    from app.api.routes import debug

    app.include_router(debug.router, prefix="/api")
