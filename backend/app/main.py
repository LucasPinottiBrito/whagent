from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, conversations, health, internal, webhooks
from app.core.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.app_debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api/auth")
app.include_router(webhooks.router, prefix="/api")
app.include_router(internal.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
